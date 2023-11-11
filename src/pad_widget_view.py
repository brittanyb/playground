import OpenGL.GL as GL

from pad_model import PadEntry, PanelEntry, SensorEntry, LEDEntry, Coord
from pad_widget_gl import Rect, TexturePainter, RectCoord


LEDDict = dict[Coord, LEDEntry]
SensorDict = dict[Coord, SensorEntry]
PanelMouseAreaDict = tuple[Coord, dict[Coord, RectCoord]]
SensorCoord = tuple[Coord, Coord] | None


class PanelPainter:
    """Painter for an arrow panels sensor and LED values."""

    SIZE = 280

    def __init__(self, coord: Coord, data: PanelEntry, rect: Rect):
        panel_pos = (coord[0] * self.SIZE, coord[1] * self.SIZE)
        self._sensors = SensorPainter(panel_pos, data.sensors, rect)
        self._leds = LEDGridPainter(panel_pos, data.leds, rect)
        self._coord = coord
        self.draw()

    def draw(self) -> None:
        self._sensors.update_thresholds()
        self._sensors.draw()
        self._leds.draw()

    @property
    def mouse_areas(self) -> PanelMouseAreaDict:
        return self._coord, self._sensors.mouse_area

    def update_sensor_thresholds(self) -> None:
        self._sensors.update_thresholds()


class LEDGridPainter:
    GRID_SIZE = 180
    GRID_OFFSET = int((PanelPainter.SIZE - GRID_SIZE) / 2)
    LED_SPACE = 2
    LED_NUM = 12
    LED_SIZE = int(GRID_SIZE / LED_NUM - LED_SPACE)
    LED_STEP = LED_SIZE + LED_SPACE

    def __init__(self, panel: Coord, data: LEDDict, rect: Rect):
        self._data = data
        self._panel_x = panel[0]
        self._panel_y = panel[1]
        self._rect = rect
        self._create_led_grid_base()

    def _create_led_grid_base(self) -> None:
        grid_x = self._panel_x + self.GRID_OFFSET
        grid_y = self._panel_y + self.GRID_OFFSET + self.GRID_SIZE
        self._base: dict[Coord, RectCoord] = {}
        for coord in self._data.keys():
            x1 = grid_x + self.LED_STEP * coord[0]
            y1 = grid_y - self.LED_SIZE - (self.LED_STEP * coord[1])
            x2 = x1 + self.LED_SIZE
            y2 = y1 + self.LED_SIZE
            self._base[coord] = (x1, y1, x2, y2)

    def draw(self) -> None:
        for coord, led in self._data.items():
            self._rect.draw(self._base[coord], (*led.colour, Rect.NO_ALPHA))


class SensorPainter:
    WIDTH = 20
    HEIGHT = 100
    POS_X1 = 5
    POS_Y1 = POS_X1
    POS_X2 = PanelPainter.SIZE - WIDTH - POS_X1
    POS_Y2 = PanelPainter.SIZE - HEIGHT - POS_Y1
    MOUSE_PAD = 5

    def __init__(self, panel: Coord, data: SensorDict, rect: Rect):
        self._data = data
        self._panel_x = panel[0]
        self._panel_y = panel[1]
        self._rect = rect
        self._create_sensors()

    def update_thresholds(self) -> None:
        for coord, sensor in self._data.items():
            if sensor.updated:
                self._threshold[coord] = self._create_threshold(coord)
                self._mouse_area[coord] = self._create_mouse_area(coord)

    def _create_sensors(self) -> None:
        self._base: dict[Coord, RectCoord] = {}
        self._threshold: dict[Coord, RectCoord] = {}
        self._mouse_area: dict[Coord, RectCoord] = {}
        for coord in self._data.keys():
            self._base[coord] = self._create_base(coord)
            self._threshold[coord] = self._create_threshold(coord)
            self._mouse_area[coord] = self._create_mouse_area(coord)

    def _create_base(self, coord: Coord) -> RectCoord:
        x_off = self.POS_X1 if coord[0] == 0 else self.POS_X2
        y_off = self.POS_Y1 if coord[1] == 1 else self.POS_Y2
        x1 = self._panel_x + x_off
        y1 = self._panel_y + y_off
        x2 = x1 + self.WIDTH
        y2 = y1 + self.HEIGHT
        return x1, y1, x2, y2

    def _create_threshold(self, coord: Coord) -> RectCoord:
        sensor = self._data[coord]
        sensor_x = self._base[coord][0]
        sensor_y = self._base[coord][1]
        x1 = sensor_x
        y1 = sensor_y + sensor.threshold - sensor.hysteresis
        x2 = sensor_x + self.WIDTH
        y2 = sensor_y + sensor.threshold
        return x1, y1, x2, y2

    def _create_mouse_area(self, coord: Coord) -> RectCoord:
        def mouse_area(index: int, vertex: int) -> int:
            if index // 2 == 0:
                padded = vertex - self.MOUSE_PAD
            else:
                padded = vertex + self.MOUSE_PAD
            lower = self._panel_x, self._panel_y
            upper = lower[0] + PanelPainter.SIZE, lower[1] + PanelPainter.SIZE
            return max(lower[index % 2], min(upper[index % 2], padded))
        threshold = self._threshold[coord]
        x1, y1, x2, y2 = (mouse_area(i, v) for i, v in enumerate(threshold))
        return x1, y1, x2, y2

    def draw(self) -> None:
        for coord, sensor in self._data.items():
            value_grad = Rect.GREEN_GRAD if sensor.active else Rect.BLUE_GRAD
            delta_val = sensor.current_value - sensor.base_value
            delta_pos = max(min(delta_val, self.HEIGHT), 0)
            abs_pos = self._base[coord][1] + delta_pos
            self._rect.draw(self._base[coord], *Rect.GRAY_GRAD)
            self._rect.draw((*self._base[coord][0:3], abs_pos), *value_grad)
            self._rect.draw(self._threshold[coord], *Rect.RED_GRAD)

    @property
    def mouse_area(self) -> dict[Coord, RectCoord]:
        return self._mouse_area


class PadPainter:
    """Painter for a dance pad."""

    SIZE = PanelPainter.SIZE * 3
    GLOSS_PATH = "../assets/gloss-texture.jpg"
    METAL_PATH = "../assets/brushed-metal-texture.jpg"

    def __init__(self, pad_data: PadEntry):
        self._pad_data = pad_data
        self._rect = Rect()

        gloss = TexturePainter.load(self.GLOSS_PATH)
        self.gloss_id = TexturePainter.set_data(*gloss)
        metal = TexturePainter.load(self.METAL_PATH)
        self.metal_id = TexturePainter.set_data(*metal)
        self.painters: list[PanelPainter] = []
        for coord, data in pad_data.panels.items():
            self.painters.append(PanelPainter(coord, data, self._rect))

    def draw_base(self) -> None:
        for coord in self._pad_data.panels.keys():
            x1 = coord[0] * PanelPainter.SIZE
            y1 = coord[1] * PanelPainter.SIZE
            x2 = x1 + PanelPainter.SIZE
            y2 = y1 + PanelPainter.SIZE
            self._rect.draw((x1, y1, x2, y2), Rect.DARK_GRAY)
        for coord in self._pad_data.blanks:
            x_pos = coord[0] * PanelPainter.SIZE
            y_pos = coord[1] * PanelPainter.SIZE
            args = self.metal_id, x_pos, y_pos, PanelPainter.SIZE, 0.5
            TexturePainter.draw(*args)

    def draw_panel_data(self) -> None:
        for painter in self.painters:
            painter.draw()

    def draw_overlay(self) -> None:
        TexturePainter.draw(self.gloss_id, 0, 0, self.SIZE, 0.2)

    def render(self) -> None:
        self._rect.render()


class PadWidgetView:
    """View class encapsulating GL framework for dance pad painters."""

    SIZE = PadPainter.SIZE

    def init_painting(self, frame_data: PadEntry) -> None:
        self._frame_data = frame_data
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        self.painter = PadPainter(self._frame_data)

    def handle_resize_event(self, w: int, h: int) -> None:
        GL.glViewport(0, 0, w, h)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, w, 0, h, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()

    def draw_widget(self) -> None:
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        self.painter.draw_base()
        self.painter.draw_panel_data()
        self.painter.draw_overlay()
        self.painter.render()

    def mouse_in_sensor_area(self, x: int, y: int) -> SensorCoord:
        for panel_coord, sensors in self.mouse_areas.items():
            for sensor_coord, (x1, y1, x2, y2) in sensors.items():
                if x1 <= x <= x2 and y1 <= y <= y2:
                    return (panel_coord, sensor_coord)
        return None

    def set_frame_data(self, frame_data: PadEntry) -> None:
        self._frame_data.set_frame_data(frame_data)

    def update_sensor_thresholds(self) -> None:
        for panel_painter in self.painter.painters:
            panel_painter.update_sensor_thresholds()

    @property
    def mouse_areas(self) -> dict[Coord, dict[Coord, RectCoord]]:
        rects = {}
        for panel_painter in self.painter.painters:
            coord, mouse_areas = panel_painter.mouse_areas
            rects[coord] = mouse_areas
        return rects
