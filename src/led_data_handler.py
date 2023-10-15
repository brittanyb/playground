import time

from reflex_controller import ReflexController


class LEDDataHandler:
    """Converts lights data from PadModel to RE:Flex Dance format."""

    def __init__(self):
        self._panel_index = -1
        self._segment_index = -1
        self._frame_index = -1

    def get_led_frame_data(self) -> int:
        self._segment_index = (self._segment_index + 1) % 4
        if self._segment_index == 0:
            self._panel_index = (self._panel_index + 1) % 4
            if self._panel_index == 0:
                self._frame_index = (self._frame_index + 1) % 16
        frame_data = self._panel_index << 6
        frame_data |= self._segment_index << 4
        frame_data |= self._frame_index
        return frame_data


if __name__ == "__main__":
    pad_controller = ReflexController()
    data_handler = LEDDataHandler()

    index = 0
    while True:
        frame_data = data_handler.get_led_frame_data()
        led_data = [0x00 for _ in range(63)]
        packet = bytes([frame_data, *led_data])
        pad_controller.lights_queue.put(packet)
