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

    def setup_frame_data(self) -> int:
        self._segment = (self._segment + 1) % self.NUM_SEGMENTS
        if self._segment == 0:
            self._panel = (self._panel + 1) % self.NUM_PANELS
            if self._panel == 0:
                self._frame = (self._frame + 1) % self.NUM_FRAMES
                if self._frame == 0:
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
            return led.green
        elif byte_index % 3 == 1:
            return led.red
        else:
            return led.blue

    def give_sample(self) -> None:
        if not self._event.is_set():
            return
        frame_byte = self.setup_frame_data()
        led_data = [self.get_data_byte(i) for i in range(63)]
        frame_data = [frame_byte, *led_data]
        with self._data.get_lock():
            for index in range(64):
                self._data[index] = frame_data[index]
        self._generator.update_led_frame()
        self._event.clear()
