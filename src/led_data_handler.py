import multiprocessing


class LEDDataHandler:
    """Converts lights data from PadModel to RE:Flex Dance format."""

    def __init__(self, light_queue: multiprocessing.Queue):
        self._light_queue = light_queue

    def give_sample(self):
        pass
