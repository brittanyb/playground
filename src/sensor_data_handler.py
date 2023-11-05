import multiprocessing
import time


from pad_model import Coord, PadModel


class SensorDataHandler:
    """Converts sensors data from RE:Flex Dance to PadModel format."""

    def __init__(self, sensor_queue: multiprocessing.Queue):
        self._sensor_queue = sensor_queue
        self._samples = 0
        self._last_time = time.time()
        self._delta = 0.0
        self._first_time = False
        self._refreshed = False
        self._pad_data = {}

    def take_sample(self):
        if not self._sensor_queue.empty():
            sensor_data = self._sensor_queue.get()
            self.organise_sensor_data(sensor_data)
            return self.count_samples()
        return None

    def organise_sensor_data(self, sensor_data: bytearray) -> None:
        for index in range(0, len(sensor_data) // 2, 2):
            panel_coord = PadModel.PANELS.coords[(index // 2) // 4]
            sensor_coord = PadModel.SENSORS.coords[(index // 2) % 4]
            sensor_value = sensor_data[index] + (sensor_data[index + 1] << 8)
            self._pad_data[(panel_coord, sensor_coord)] = sensor_value

    def count_samples(self) -> float | None:
        if self._first_time == False:
            self._refreshed = True
            self._last_time = time.time()
            self._first_time = True
            return None
        self._samples += 1
        if self._samples % 1000 == 0:
            current_time = time.time()
            self._delta += current_time - self._last_time - 1
            self._last_time = current_time
            return self._delta

    @property
    def pad_data(self) -> dict[tuple[Coord, Coord], int]:
        return self._pad_data.copy()

    @property
    def refreshed(self) -> bool:
        if self._refreshed:
            self._refreshed = False
            return True
        else:
            return False
