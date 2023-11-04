import ctypes

import OpenGL.GL as GL
import PIL.Image as Image


Quad = tuple[int, int, int, int]
Rgba = tuple[int, int, int, int] | None
RectCoord = tuple[int, int, int, int]
Gradient = tuple[Rgba, Rgba]


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
        min_args = GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR
        mag_args = GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR
        GL.glTexParameteri(*min_args)
        GL.glTexParameteri(*mag_args)
        texture_params = GL.GL_TEXTURE_2D, 0, GL.GL_RGBA
        dimensions = width, height, 0
        pixel_data = GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, image_data
        GL.glTexImage2D(*texture_params, *dimensions, *pixel_data)
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


class Rect:
    """Painter for a rectangle with a colour gradient."""

    NO_ALPHA = 255
    DARK_GRAY = (10, 10, 10, NO_ALPHA)
    MID_GRAY = (100, 100, 100, NO_ALPHA)
    LIGHT_GRAY = (200, 200, 200, NO_ALPHA)
    LIGHT_RED = (150, 0, 0, 175)
    DARK_RED = (50, 0, 0, 175)
    LIGHT_GREEN = (0, 200, 0, NO_ALPHA)
    DARK_GREEN = (0, 100, 0, NO_ALPHA)
    LIGHT_BLUE = (0, 0, 200, NO_ALPHA)
    DARK_BLUE = (0, 0, 100, NO_ALPHA)

    GRAY_GRAD = (LIGHT_GRAY, MID_GRAY)
    RED_GRAD = (LIGHT_RED, DARK_RED)
    GREEN_GRAD = (LIGHT_GREEN, DARK_GREEN)
    BLUE_GRAD = (LIGHT_BLUE, DARK_BLUE)

    NUM_BYTES = 4

    def __init__(self):
        self._vertex_data = []
        self.create_vbo()

    def draw(self, rect: RectCoord, col: Rgba, grad: Rgba = None) -> None:
        if not col:
            return
        self._vertex_data.extend(rect)
        vert_range = range(len(rect))
        colour = [grad if grad and i % 2 == 0 else col for i in vert_range]
        for vertex_id in vert_range:
            self._vertex_data.append(rect[vertex_id])
            self._vertex_data.extend(colour[vertex_id])

    def create_vbo(self):
        self._vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self._vbo)
        array_type = ctypes.c_float * len(self._vertex_data)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, len(self._vertex_data) * 4,
                        array_type(*self._vertex_data), GL.GL_STATIC_DRAW)

    def render(self):
        if self._vbo is None:
            self.create_vbo()
        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
        GL.glEnableClientState(GL.GL_COLOR_ARRAY)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self._vbo)
        stride = 6 * 4
        GL.glVertexPointer(2, GL.GL_FLOAT, stride, ctypes.c_void_p(0))
        GL.glColorPointer(4, GL.GL_FLOAT, stride, ctypes.c_void_p(2 * 4))
        GL.glDrawArrays(GL.GL_QUADS, 0, len(self._vertex_data) // 6)
        GL.glDisableClientState(GL.GL_VERTEX_ARRAY)
        GL.glDisableClientState(GL.GL_COLOR_ARRAY)
