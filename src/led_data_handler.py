from multiprocessing.sharedctypes import SynchronizedArray
from multiprocessing.synchronize import Event

from led_data_generator import LEDDataGenerator
from pad_model import PadModel


class LEDDataHandler:
    """Converts lights data from PadModel to RE:Flex Dance format."""

    NUM_SEGMENTS = 4
    NUM_PANELS = 4
    NUM_FRAMES = 16
    NUM_LEDS = 21

    GAMMA = [
        0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
        0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
        1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   2,
        2,   2,   2,   2,   2,   2,   2,   3,   3,   3,   3,   3,   3,   3,
        4,   4,   4,   4,   4,   5,   5,   5,   5,   6,   6,   6,   6,   7,
        7,   7,   7,   8,   8,   8,   9,   9,   9,  10,   10,  10,  11,  11,
        11,  12,  12,  13,  13,  13,  14,  14,  15,  15,  16,  16,  17,  17,
        18,  18,  19,  19,  20,  20,  21,  21,  22,  22,  23,  24,  24,  25,
        25,  26,  27,  27,  28,  29,  29,  30,  31,  32,  32,  33,  34,  35,
        35,  36,  37,  38,  39,  39,  40,  41,  42,  43,  44,  45,  46,  47,
        48,  49,  50,  50,  51,  52,  54,  55,  56,  57,  58,  59,  60,  61,
        62,  63,  64,  66,  67,  68,  69,  70,  72,  73,  74,  75,  77,  78,
        79,  81,  82,  83,  85,  86,  87,  89,  90,  92,  93,  95,  96,  98,
        99,  101, 102, 104, 105, 107, 109, 110, 112, 114, 115, 117, 119, 120,
        122, 124, 126, 127, 129, 131, 133, 135, 137, 138, 140, 142, 144, 146,
        148, 150, 152, 154, 156, 158, 160, 162, 164, 167, 169, 171, 173, 175,
        177, 180, 182, 184, 186, 189, 191, 193, 196, 198, 200, 203, 205, 208,
        210, 213, 215, 218, 220, 223, 225, 228, 231, 233, 236, 239, 241, 244,
        247, 249, 252, 255
    ]
    POSITIONS = [
        [
            (5, 0), (5, 1), (4, 1), (5, 2), (4, 2), (3, 2), (5, 3),
            (4, 3), (3, 3), (2, 3), (5, 4), (4, 4), (3, 4), (2, 4),
            (1, 4), (5, 5), (4, 5), (3, 5), (2, 5), (1, 5), (0, 5)
        ],
        [
            (6, 0), (7, 1), (6, 1), (8, 2), (7, 2), (6, 2), (9, 3),
            (8, 3), (7, 3), (6, 3), (10, 4), (9, 4), (8, 4), (7, 4),
            (6, 4), (11, 5), (10, 5), (9, 5), (8, 5), (7, 5), (6, 5)
        ],
        [
            (6, 11), (7, 10), (6, 10), (8, 9),  (7, 9), (6, 9), (9, 8),
            (8, 8),  (7, 8),  (6, 8),  (10, 7), (9, 7), (8, 7), (7, 7),
            (6, 7),  (11, 6), (10, 6), (9, 6),  (8, 6), (7, 6), (6, 6)
        ],
        [
            (5, 11), (5, 10), (4, 10), (5, 9), (4, 9), (3, 9), (5, 8),
            (4, 8),  (3, 8),  (2, 8),  (5, 7), (4, 7), (3, 7), (2, 7),
            (1, 7),  (5, 6),  (4, 6),  (3, 6), (2, 6), (1, 6), (0, 6)
        ]
    ]

    def __init__(self, data: SynchronizedArray, event: Event, model: PadModel):
        self._data = data
        self._generator = LEDDataGenerator(model)
        self._event = event
        self._model = model
        self._segment = -1
        self._panel = -1
        self._frame = -1
        self._led_data = {}
        self._frame_change = False

    def setup_frame_data(self) -> int:
        self._segment = (self._segment + 1) % self.NUM_SEGMENTS
        if self._segment == 0:
            self._panel = (self._panel + 1) % self.NUM_PANELS
            if self._panel == 0:
                self._frame_change = True
                self._frame = (self._frame + 1) % self.NUM_FRAMES
                self._led_data = self._model.get_led_data()

        return (self._panel << 6) | (self._segment << 4) | (self._frame)

    def get_data_byte(self, byte_index: int) -> int:
        panel_coord = PadModel.PANELS.coords[self._panel]
        if (panel_data := self._led_data.get(panel_coord, None)) is None:
            return 0
        led_index = (byte_index // 3)
        led_coord = self.POSITIONS[self._segment][led_index]
        led = panel_data[led_coord]
        if byte_index % 3 == 0:
            col = led.green
        elif byte_index % 3 == 1:
            col = led.red
        else:
            col = led.blue
        return self.GAMMA[col]

    def give_sample(self) -> None:
        if not self._event.is_set():
            return
        frame_byte = self.setup_frame_data()
        led_data = [self.get_data_byte(i) for i in range(63)]
        frame_data = [frame_byte, *led_data]
        with self._data.get_lock():
            for index in range(64):
                self._data[index] = frame_data[index]
        if self._frame_change:
            self._generator.update_led_frame()
            self._frame_change = False
        self._event.clear()
