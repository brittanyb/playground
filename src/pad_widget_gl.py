import ctypes

import numpy as np
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


class RectShader:
    VERT = """
#version 330 core
#extension GL_ARB_separate_shader_objects : enable

layout(location = 0) in vec2 aPos;
layout(location = 1) in vec4 aColor;

layout(location = 0) out vec4 vertexColor;

const float maxX = 840.0;
const float maxY = 840.0;
const float maxC = 255.0;

void main() {
    float normalizedX = (aPos.x / maxX) * 2.0 - 1.0;
    float normalizedY = (aPos.y / maxY) * 2.0 - 1.0;
    gl_Position = vec4(normalizedX, normalizedY, 0.0, 1.0);
    vertexColor = aColor / maxC;
}
"""

    FRAG = """
#version 330 core

in vec4 vertexColor;
out vec4 FragColor;

void main() {
    FragColor = vertexColor;
}
    """

    def __init__(self):
        vert = self.compile_shader(self.VERT, GL.GL_VERTEX_SHADER)
        frag = self.compile_shader(self.FRAG, GL.GL_FRAGMENT_SHADER)
        self.program = GL.glCreateProgram()
        GL.glAttachShader(self.program, vert)
        GL.glAttachShader(self.program, frag)
        GL.glLinkProgram(self.program)
        GL.glDeleteShader(vert)
        GL.glDeleteShader(frag)

    def compile_shader(self, source: str, shader_type):
        shader = GL.glCreateShader(shader_type)
        GL.glShaderSource(shader, source)
        GL.glCompileShader(shader)

        if not GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS):
            info: bytes = GL.glGetShaderInfoLog(shader)
            raise Exception(info.decode())

        return shader


class Rect:
    """Painter for rectangles with colour gradients."""

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

    UINT32_BYTES = 4
    VERTEX_LEN = 6
    STRIDE = UINT32_BYTES * VERTEX_LEN

    def __init__(self):
        self._vertex_data = []
        self._shader = RectShader()
        self._vao = None

    def draw(self, rect: RectCoord, col: Rgba, grad: Rgba = None) -> None:
        if col is None:
            return
        self._vertex_data.extend([rect[0], rect[3]])
        self._vertex_data.extend(grad if grad else col)
        self._vertex_data.extend([rect[0], rect[1]])
        self._vertex_data.extend(col)
        self._vertex_data.extend([rect[2], rect[3]])
        self._vertex_data.extend(col)
        self._vertex_data.extend([rect[2], rect[3]])
        self._vertex_data.extend(col)
        self._vertex_data.extend([rect[0], rect[1]])
        self._vertex_data.extend(col)
        self._vertex_data.extend([rect[2], rect[1]])
        self._vertex_data.extend(grad if grad else col)

    def create_vbo(self):
        dat = np.array(self._vertex_data, dtype=np.float32)
        self._vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self._vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, dat.nbytes,
                        dat, GL.GL_STATIC_DRAW)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

    def setup_attribs(self, idx: int, size: int):
        val_t = GL.GL_FLOAT
        norm = GL.GL_FALSE
        pointer = ctypes.c_void_p(idx * 4 * 2)
        GL.glEnableVertexAttribArray(idx)
        GL.glVertexAttribPointer(idx, size, val_t, norm, self.STRIDE, pointer)

    def create_vao(self):
        self._vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self._vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self._vbo)
        self.setup_attribs(0, 2)
        self.setup_attribs(1, 4)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

    def render(self):
        if self._vao is None:
            self.create_vbo()
            self.create_vao()
        dat = np.array(self._vertex_data, dtype=np.float32)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self._vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, dat.nbytes,
                        dat, GL.GL_STATIC_DRAW)
        num_to_draw = len(self._vertex_data) // 6
        GL.glUseProgram(self._shader.program)
        GL.glBindVertexArray(self._vao)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, num_to_draw)
        GL.glBindVertexArray(0)
        GL.glUseProgram(0)
        self._vertex_data = []
