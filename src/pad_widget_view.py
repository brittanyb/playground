import OpenGL.GL as GL
import PIL.Image as Image

from pad_model import (
    PadEntry, PanelEntry, SensorEntry, LEDEntry, Colour, Coord
)


Quad = tuple[int, int, int, int]
RGBAValue = tuple[int, int, int, int]
RectCoord = tuple[Coord, Coord]


class TexturePainter:
    """Generic painter to map texture images to quads."""

    @staticmethod
    def load(path: str) -> tuple[bytes, int, int]:
        image = Image.open(path)
        conv_image = image.convert("RGBA")
        image_data = conv_image.transpose(Image.FLIP_TOP_BOTTOM).tobytes()
        image.close()
        return (image_data, image.width, image.height)

    @staticmethod
    def set_data(image_data: bytes, width: int, height: int) -> int:
        texture_id = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)
        GL.glTexParameteri(
            GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR
        )
        GL.glTexParameteri(
            GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR
        )
        GL.glTexImage2D(
            GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, width, height, 0,
            GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, image_data
        )
        return texture_id

    @staticmethod
    def draw(id: int, x: int, y: int, size: int, alpha: float) -> None:
        GL.glEnable(GL.GL_TEXTURE_2D)
        GL.glBindTexture(GL.GL_TEXTURE_2D, id)
        GL.glColor4f(1.0, 1.0, 1.0, alpha)
        GL.glBegin(GL.GL_QUADS)
        for cx, cy in [(0, 0), (1, 0), (1, 1), (0, 1)]:
            GL.glTexCoord2f(cx, cy)
            GL.glVertex2f(x + size * cx, y + size * cy)
        GL.glEnd()
        GL.glDisable(GL.GL_TEXTURE_2D)


class RectPainter:
    """Painter for a rectangle with a colour gradient."""

    DARK_GRAY = (10, 10, 10, 255)
    MID_GRAY = (100, 100, 100, 255)
    LIGHT_GRAY = (200, 200, 200, 255)
    LIGHT_RED = (150, 0, 0, 175)
    DARK_RED = (50, 0, 0, 175)
    LIGHT_GREEN = (0, 200, 0, 255)
    DARK_GREEN = (0, 100, 0, 255)
    LIGHT_BLUE = (0, 0, 200, 255)
    DARK_BLUE = (0, 0, 100, 255)

    @staticmethod
    def draw(
        x: int, y: int, w: int, h: int, start_col: RGBAValue | Colour,
        end_col: RGBAValue | Colour | None = None
    ) -> None:
        GL.glBegin(GL.GL_QUADS)
        if len(start_col) == 3:
            GL.glColor3ub(*start_col)
        else:
            GL.glColor4ub(*start_col)
        GL.glVertex2f(x, y)
        GL.glVertex2f(x + w, y)
        if end_col is not None:
            if len(end_col) == 3:
                GL.glColor3ub(*end_col)
            elif len(end_col) == 4:
                GL.glColor4ub(*end_col)
        GL.glVertex2f(x + w, y + h)
        GL.glVertex2f(x, y + h)
        GL.glEnd()


class PanelPainter:
    """Painter for an arrow panels sensor and LED values."""

    SIZE = 280
    SEN_WIDTH = 15
    SEN_HEIGHT = 100
    SEN_SPACE = 5
    LED_GRID_SIZE = 180
    LED_SPACE = 2
    LED_SIZE = int(LED_GRID_SIZE / 12 - LED_SPACE)
    RECT_PAD = 5

    def __init__(self, coord: Coord, data: PanelEntry):
        self._offset = (coord[0] * self.SIZE, coord[1] * self.SIZE)
        self._l_offset = (
            int(self._offset[0] + ((self.SIZE - self.LED_GRID_SIZE) / 2)),
            int(self._offset[1] + ((self.SIZE - self.LED_GRID_SIZE) / 2))
        )
        self._coord = coord
        self._data = data
        self._threshold_rects = {}
        self.draw()

    def draw(self) -> None:
        for coord, data in self._data.sensors.items():
            self.draw_sensor(coord, data)
        for coord, data in self._data.leds.items():
            self.draw_led(coord, data)

    def draw_led(self, coord: Coord, data: LEDEntry) -> None:
        x = self._l_offset[0] + (self.LED_SIZE + self.LED_SPACE) * coord[0]
        y = self._l_offset[1] + (self.LED_SIZE + self.LED_SPACE) * coord[1]
        RectPainter.draw(x, y, self.LED_SIZE, self.LED_SIZE, data.colour)

    def draw_sensor(self, coord: Coord, data: SensorEntry) -> None:
        if (coord[0] == 0):
            x = self._offset[0] + self.SEN_SPACE
        else:
            x = self._offset[0] + self.SIZE - self.SEN_WIDTH - self.SEN_SPACE
        if (coord[1] == 0):
            y = self._offset[1] + self.SIZE - self.SEN_HEIGHT - self.SEN_SPACE
        else:
            y = self._offset[1] + self.SEN_SPACE
        self.store_rect(coord, data, x, y)
        if data.active:
            s_col = RectPainter.LIGHT_GREEN
            e_col = RectPainter.DARK_GREEN
        else:
            s_col = RectPainter.LIGHT_BLUE
            e_col = RectPainter.DARK_BLUE
        delta = data.current_value - data.base_value
        off = data.threshold - data.hysteresis
        range = data.threshold - off
        RectPainter.draw(
            x, y, self.SEN_WIDTH, self.SEN_HEIGHT,
            RectPainter.LIGHT_GRAY, RectPainter.MID_GRAY
        )
        RectPainter.draw(x, y, self.SEN_WIDTH, delta, s_col, e_col)
        RectPainter.draw(
            x, y + off, self.SEN_WIDTH, range,
            RectPainter.LIGHT_RED, RectPainter.DARK_RED
        )

    @property
    def threshold_rects(
        self
    ) -> dict[tuple[int, int], dict[tuple[int, int], list[int]]]:
        return self._threshold_rects

    def store_rect(
            self, coord: Coord, data: SensorEntry, x: int, y: int
    ) -> None:
        x1 = max(x - self.RECT_PAD, 0)
        y1 = max(y + data.threshold - data.hysteresis - self.RECT_PAD, 0)
        x2 = max(x + self.SEN_WIDTH + self.RECT_PAD, 0)
        y2 = max(y + data.threshold + self.RECT_PAD, 0)
        if not self._coord in self._threshold_rects:
            self._threshold_rects[self._coord] = {}
        self._threshold_rects[self._coord][coord] = [x1, y1, x2, y2]


class PadPainter:
    """Painter for a dance pad."""

    SIZE = PanelPainter.SIZE * 3
    GLOSS_PATH = "../assets/gloss-texture.jpg"
    METAL_PATH = "../assets/brushed-metal-texture.jpg"

    def __init__(self, pad_data: PadEntry):
        gloss = TexturePainter.load(self.GLOSS_PATH)
        self.gloss_id = TexturePainter.set_data(*gloss)
        metal = TexturePainter.load(self.METAL_PATH)
        self.metal_id = TexturePainter.set_data(*metal)
        self._pad_data = pad_data
        self.painters = [
            PanelPainter(coord, data)
            for coord, data in pad_data.panels.items()
        ]

    def draw_base(self) -> None:
        RectPainter.draw(0, 0, self.SIZE, self.SIZE, RectPainter.DARK_GRAY)
        for blank in self._pad_data.blanks:
            x_pos = blank[0] * PanelPainter.SIZE
            y_pos = blank[1] * PanelPainter.SIZE
            TexturePainter.draw(
                self.metal_id, x_pos, y_pos, PanelPainter.SIZE, 0.5
            )

    def draw_panel_data(self) -> None:
        for painter in self.painters:
            painter.draw()

    def draw_overlay(self) -> None:
        TexturePainter.draw(self.gloss_id, 0, 0, self.SIZE, 0.2)


class PadWidgetView:
    """View class encapsulating GL framework for dance pad painters."""

    SIZE = PadPainter.SIZE

    def init_painting(self, frame_data: PadEntry) -> None:
        self._frame_data = frame_data
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glOrtho(0, self.SIZE, 0, self.SIZE, -1, 1)
        self.painter = PadPainter(self._frame_data)

    def handle_resize_event(self, w: int, h: int) -> None:
        GL.glViewport(0, 0, w, h)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, w, 0, h, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        self.painter.draw_base()

    def draw_widget(self) -> None:
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        self.painter.draw_base()
        self.painter.draw_panel_data()
        self.painter.draw_overlay()

    @property
    def threshold_rects(self) -> dict[Coord, dict]:
        rects = {}
        for panel_painter in self.painter.painters:
            rects.update(panel_painter.threshold_rects)
        return rects

    def mouse_in_threshold_rect(self, x: int, y: int) -> RectCoord | None:
        for panel_coord, sensor_dict in self.threshold_rects.items():
            for sensor_coord, [x1, y1, x2, y2] in sensor_dict.items():
                if x1 <= x <= x2 and y1 <= y <= y2:
                    return (panel_coord, sensor_coord)
        return None

    def set_frame_data(self, frame_data: PadEntry) -> None:
        self._frame_data.set_frame_data(frame_data)
