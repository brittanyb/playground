import dataclasses

import keyboard

Coord = tuple[int, int]
Colour = tuple[int, int, int]
BlankData = list[Coord]
ProfilePanelData = tuple[dict[Coord, tuple[int, int]], str]
ProfilePadData = dict[Coord, ProfilePanelData]


@dataclasses.dataclass
class Coords:
    coords: list[Coord]


@dataclasses.dataclass
class LEDEntry:
    B8_MAX = 255

    red: int = 0
    green: int = 0
    blue: int = 0

    @property
    def colour(self) -> Colour:
        return (self.red, self.green, self.blue)

    @colour.setter
    def colour(self, colour: Colour):
        self.red = int(max(0, min(colour[0], self.B8_MAX)))
        self.green = int(max(0, min(colour[1], self.B8_MAX)))
        self.blue = int(max(0, min(colour[2], self.B8_MAX)))


@dataclasses.dataclass
class SensorEntry:
    MAX_ON = 100
    MAX_OFF = MAX_ON - 1
    B12_MAX = 4095
    MAX_BASE = B12_MAX - MAX_ON

    base_value: int = 0
    current_value: int = 0
    threshold: int = 30
    hysteresis: int = 5
    updated: bool = True
    _active: bool = False

    def set_base_value(self, base_value: int):
        self.base_value = int(max(0, min(base_value, self.B12_MAX)))

    def set_current_value(self, current_value: int):
        self.current_value = int(max(0, min(current_value, self.MAX_BASE)))
        self.set_active()

    def set_threshold(self, threshold: int):
        self.threshold = int(max(self.hysteresis, min(threshold, self.MAX_ON)))

    def set_hysteresis(self, hysteresis: int):
        self.hysteresis = int(max(1, min(hysteresis, self.threshold)))

    def set_active(self):
        delta = self.current_value - self.base_value
        pressed = delta >= self.threshold
        released = delta <= self.threshold - self.hysteresis
        if not self._active and pressed:
            self._active = True
        elif self._active and released:
            self._active = False

    @property
    def active(self) -> bool:
        return self._active

    @property
    def profile_data(self) -> tuple[int, int]:
        return (self.threshold, self.hysteresis)

    @profile_data.setter
    def profile_data(self, data: tuple[int, int]):
        self.threshold = data[0]
        self.hysteresis = data[1]


@dataclasses.dataclass
class PanelEntry:
    sensors: dict[Coord, SensorEntry]
    leds: dict[Coord, LEDEntry]
    key_val: str
    pressed: bool = False

    def __init__(self, sensors: Coords, leds: Coords, key_val: str):
        self.sensors = {coord: SensorEntry() for coord in sensors.coords}
        self.leds = {coord: LEDEntry() for coord in leds.coords}
        self.key_val = key_val

    @property
    def active(self) -> bool:
        for sensor in self.sensors.values():
            if sensor.active:
                return True
        return False

    @property
    def profile_data(self) -> ProfilePanelData:
        sensor_data = {
            coord: sensor.profile_data
            for coord, sensor in self.sensors.items()
        }
        return (sensor_data, self.key)

    @property
    def key(self) -> str:
        return self.key_val

    @key.setter
    def key(self, key_val: str):
        self.key_val = key_val

    @profile_data.setter
    def profile_data(self, panel_data: ProfilePanelData):
        self._profile_set = False
        for coord, data in self.sensors.items():
            data.profile_data = panel_data[0][coord]
        self.key_val = panel_data[1]

    def set_frame_data(self, panel_data: "PanelEntry") -> None:
        for coord, sensor in self.sensors.items():
            sensor.set_base_value(panel_data.sensors[coord].base_value)
            sensor.set_current_value(panel_data.sensors[coord].current_value)
            sensor.set_hysteresis(panel_data.sensors[coord].hysteresis)
            sensor.set_threshold(panel_data.sensors[coord].threshold)
        for coord, led in self.leds.items():
            led.colour = panel_data.leds[coord].colour


SensorCoord = tuple[Coord, Coord]


@dataclasses.dataclass
class PadEntry:
    blanks: list[Coord]
    panels: dict[Coord, PanelEntry]

    def __init__(
            self, blanks: Coords, panels: Coords, sensors: Coords,
            leds: Coords, keys: list[str]
    ):
        self.blanks = blanks.coords
        self.panels = {
            coord: PanelEntry(sensors, leds, key)
            for coord, key in zip(panels.coords, keys)
        }
        self.updated = False

    @property
    def profile_data(self):
        return {
            coord: panel.profile_data for coord, panel in self.panels.items()
        }

    @profile_data.setter
    def profile_data(self, pad_data: ProfilePadData):
        for coord, data in self.panels.items():
            data.profile_data = pad_data[coord]

    def set_frame_data(self, pad_entry: "PadEntry") -> None:
        self.blanks = pad_entry.blanks
        for coord, panel in self.panels.items():
            panel.set_frame_data(pad_entry.panels[coord])

    def set_keys(self, keys: list[str]) -> None:
        for panel, key in zip(self.panels.values(), keys):
            panel.key = key


class PadModel:
    """Encapsulating class for panels."""

    @staticmethod
    def led_coords():
        GRID_LAYOUT = [
            [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0]
        ]
        coords = []
        for y, row in enumerate(GRID_LAYOUT):
            for x, value in enumerate(row):
                if value != 0:
                    coords.append((x, y))
        return coords

    BLANKS = Coords([(0, 0), (0, 2), (1, 1), (2, 0), (2, 2)])
    PANELS = Coords([(0, 1), (1, 0), (1, 2), (2, 1)])
    SENSORS = Coords([(1, 1), (1, 0), (0, 1), (0, 0)])
    LEDS = Coords(led_coords())
    KEYS = ['A', 'B', 'C', 'D']

    def __init__(self):
        self.set_default()

    def get_model_data(self) -> PadEntry:
        return self._model

    def get_led_data(self) -> dict[Coord, dict[Coord, LEDEntry]]:
        return {c: p.leds for c, p in self._model.panels.items()}

    def set_sensor(self, data: tuple[int, int, SensorCoord]) -> bool:
        self._model.updated = True
        sensor = self._model.panels[data[2][0]].sensors[data[2][1]]
        sensor.updated = True
        if data[0] == 0:
            sensor.set_threshold(sensor.threshold + data[1])
        elif data[0] == 1:
            sensor.set_hysteresis(sensor.hysteresis - data[1])
        return True

    def set_baseline(self, data: dict[tuple[Coord, Coord], int]) -> None:
        for coords, value in data.items():
            panel = coords[0]
            sensor = coords[1]
            self._model.panels[panel].sensors[sensor].set_base_value(value)

    def set_sensor_data(self, data: dict[tuple[Coord, Coord], int]) -> None:
        for coords, value in data.items():
            panel = coords[0]
            sensor = coords[1]
            self._model.panels[panel].sensors[sensor].set_current_value(value)
        for panel in self._model.panels.values():
            if panel.active and not panel.pressed:
                panel.pressed = True
                keyboard.press(panel.key)
            if not panel.active and panel.pressed:
                panel.pressed = False
                keyboard.release(panel.key)

    def set_saved(self) -> None:
        self._model.updated = False

    def set_default(self) -> None:
        self._model = PadEntry(
            self.BLANKS, self.PANELS, self.SENSORS, self.LEDS, self.KEYS
        )

    def view_updated(self) -> None:
        for panel in self._model.panels.values():
            for sensor in panel.sensors.values():
                sensor.updated = False

    def keys_updated(self, keys: list[str]) -> None:
        self._model.set_keys(keys)

    @property
    def profile_data(self) -> dict:
        self.set_saved()
        return self._model.profile_data

    @profile_data.setter
    def profile_data(self, profile_data: ProfilePadData) -> None:
        self.set_saved()
        self._model.profile_data = profile_data
