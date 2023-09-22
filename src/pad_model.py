import numpy as np


class LEDModel:
    """State management for an LED."""

    B8_MAX = 255

    def __init__(self, coord: tuple[int, int]):
        self._colour = [0, 0, 0]
        self._coord = coord

    @property
    def colour(self) -> list[int]:
        return self._colour

    @colour.setter
    def colour(self, colour: list[int]):
        r = np.clip(colour[0], 0, self.B8_MAX)
        g = np.clip(colour[1], 0, self.B8_MAX)
        b = np.clip(colour[2], 0, self.B8_MAX)
        self._colour = [r, g, b]

    @property
    def coord(self) -> tuple[int, int]:
        return self._coord


class SensorModel:
    """State management for a sensor."""

    MAX_ON = 100
    MAX_OFF = MAX_ON - 1
    B12_MAX = 4095
    MAX_BASE = B12_MAX - MAX_ON

    def __init__(self, coord: tuple[int, int]):
        self._base_value = 0
        self._current_value = 0
        self._threshold = 0
        self._hysteresis = 1
        self._active = False
        self._coord = coord

    @property
    def base_value(self) -> int:
        return self._base_value

    @base_value.setter
    def base_value(self, base_value: int):
        self._base_value = np.clip(base_value, 0, self.B12_MAX)

    @property
    def current_value(self) -> int:
        return self._current_value

    @current_value.setter
    def current_value(self, current_value: int):
        self._current_value = np.clip(current_value, 0, self.MAX_BASE)

    @property
    def delta_value(self) -> int:
        return self._current_value - self._base_value

    @property
    def threshold(self) -> int:
        return self._threshold

    @threshold.setter
    def threshold(self, threshold: int):
        self._threshold = np.clip(
            threshold, self.hysteresis, self.MAX_ON)

    @property
    def hysteresis(self) -> int:
        return self._hysteresis

    @hysteresis.setter
    def hysteresis(self, hysteresis: int):
        self._hysteresis = np.clip(
            hysteresis, 1, self.threshold
        )

    @property
    def off_threshold(self):
        return self.threshold - self.hysteresis

    @property
    def active(self) -> bool:
        delta_on = self._threshold - self._base_value
        delta_off = self._base_value + self.threshold - self._hysteresis
        pressed = self._current_value >= delta_on
        released = self._current_value <= delta_off
        if ((not self._active) & pressed):
            self._active = True
        elif (self._active & released):
            self._active = False
        return self._active

    @property
    def coord(self) -> tuple[int, int]:
        return self._coord


class LEDGridModel:
    """State management for LEDs on a given panel."""

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

    def __init__(self):
        self.leds = []
        for y_pos in range(len(self.GRID_LAYOUT)):
            for x_pos in range(len(self.GRID_LAYOUT[0])):
                if self.GRID_LAYOUT[y_pos][x_pos] != 0:
                    led = LEDModel((x_pos, y_pos))
                    self.leds.append(led)


class PanelModel:
    """Encapsulating class for sensors and lights."""

    SENSOR_COORDS = [(1, 0), (1, 1), (0, 0), (0, 1)]

    def __init__(self, panel_coord: tuple[int, int]):
        self._coord = panel_coord
        self._sensors = [SensorModel(coord) for coord in self.SENSOR_COORDS]
        self._led_grid = LEDGridModel()

    def sensor_at_coord(self, coord: tuple[int, int]) -> SensorModel | None:
        for sensor in self._sensors:
            if sensor.coord == coord:
                return sensor
        return None

    @property
    def pressed(self) -> bool:
        _pressed = False
        for sensor in self._sensors:
            if sensor.active:
                _pressed = True
        return _pressed

    @property
    def sensors(self) -> list[SensorModel]:
        return self._sensors

    @property
    def leds(self) -> list[LEDModel]:
        return self._led_grid.leds

    @property
    def coord(self) -> tuple[int, int]:
        return self._coord


class PadModel:
    """Encapsulating class for panels."""

    BLANK_COORDS = [(0, 0), (0, 2), (1, 1), (2, 0), (2, 2)]
    PANEL_COORDS = [(0, 1), (1, 0), (1, 2), (2, 1)]

    def __init__(self):
        self._panels = [PanelModel(coord) for coord in self.PANEL_COORDS]

    def panel_at_coord(self, coord: tuple[int, int]) -> PanelModel | None:
        for panel in self._panels:
            if panel.coord == coord:
                return panel
        return None

    @property
    def panels(self) -> list[PanelModel]:
        return self._panels
