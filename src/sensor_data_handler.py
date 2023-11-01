import multiprocessing
import time


class SensorDataHandler:
    """Converts sensors data from RE:Flex Dance to PadModel format."""

    def __init__(self, sensor_queue: multiprocessing.Queue):
        self._sensor_queue = sensor_queue
        self._samples = 0
        self._last_time = time.time()

    def take_sample(self):
        if not self._sensor_queue.empty():
            self._sensor_queue.get()
            self._samples += 1
            if self._samples % 1000 == 0:
                current_time = time.time()
                print(f"1k samples in: {current_time - self._last_time}s")
                self._last_time = current_time
