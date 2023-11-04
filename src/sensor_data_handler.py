import multiprocessing
import time


class SensorDataHandler:
    """Converts sensors data from RE:Flex Dance to PadModel format."""

    def __init__(self, sensor_queue: multiprocessing.Queue):
        self._sensor_queue = sensor_queue
        self._samples = 0
        self._last_time = time.time()
        self._delta = 0
        self._first_time = False

    def take_sample(self):
        if not self._sensor_queue.empty():
            self._sensor_queue.get()
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
