import multiprocessing
import time


class LEDDataHandler:
    """Converts lights data from PadModel to RE:Flex Dance format."""

    def __init__(self, light_queue: multiprocessing.Queue):
        self._light_queue = light_queue
        self._samples = 0
        self._last_time = time.time()
        self._delta = 0
        self._first_time = False

    def give_sample(self):
        if self._light_queue.empty():
            self._light_queue.put(bytearray(64))
            return self.count_samples()
        return None

    def count_samples(self):
        self._samples += 1
        if self._samples % 1000 == 0:
            if self._first_time == False:
                self._last_time = time.time()
                self._first_time = True
                return None
            current_time = time.time()
            self._delta += current_time - self._last_time - 1
            self._last_time = current_time
            return self._delta
