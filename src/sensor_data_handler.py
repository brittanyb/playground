from multiprocessing.sharedctypes import SynchronizedArray
from multiprocessing.synchronize import Event

from pad_model import Coord, PadModel


class SensorDataHandler:
    """Converts sensors data from RE:Flex Dance to PadModel format."""

    def __init__(self, data: SynchronizedArray, event: Event):
        self._data = data
        self._event = event
        self._refreshed = False
        self._initialised = False
        self._pad_data = {}

    def take_sample(self) -> None:
        if not self._event.is_set():
            return
        with self._data.get_lock():
            self.organise_sensor_data(self._data)
        if not self._initialised:
            self._initialised = True
            self._refreshed = True
        self._event.clear()

    def organise_sensor_data(self, sensor_data: SynchronizedArray) -> None:
        for index in range(0, len(sensor_data) // 2, 2):
            panel_coord = PadModel.PANELS.coords[(index // 2) // 4]
            sensor_coord = PadModel.SENSORS.coords[(index // 2) % 4]
            sensor_value = sensor_data[index] + (sensor_data[index + 1] << 8)
            self._pad_data[(panel_coord, sensor_coord)] = sensor_value

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
