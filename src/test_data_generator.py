import PySide6.QtCore as QtCore
import math

from pad_model import PadModel
from pad_widget_controller import PadWidgetController


class TestPadWidget:
    """Dummy data to test pad widget animations."""

    def __init__(self, model: PadModel, controller: PadWidgetController):
        self.t = 0
        self.timer = QtCore.QTimer()
        self.timer.setInterval(16)
        self.timer.timeout.connect(self.update)
        self.timer.start()
        self.model = model
        self.view = controller
        for p_i, panel in enumerate(self.model.panels):
            for s_i, sensor in enumerate(panel.sensors):
                threshold = int((s_i + p_i * 4) * 90 / 16 + 10)
                sensor.threshold = threshold
                sensor.hysteresis = 5

    def update(self) -> None:
        self.t += 1
        for p_i, panel in enumerate(self.model.panels):
            for led in panel.leds:
                led.colour = self.get_led_colour(*led.coord, self.t, p_i)
            for s_i, sensor in enumerate(panel.sensors):
                amp = self.get_sensor_amplitude(s_i, self.t)
                sensor.base_value = 0
                sensor.current_value = amp
        self.view.update()

    def get_led_colour(self, y: int, x: int, t: int, d: int) -> list[int]:
        phase_multiplier = 0.005
        phase_offset = t * phase_multiplier
        dir_phase_x = 0
        dir_phase_y = 0
        if d == 3:
            dir_phase_x = x * 0.01
            dir_phase_y = y * 0.05
        elif d == 2:
            dir_phase_x = x * 0.05
            dir_phase_y = y * 0.01
        elif d == 1:
            dir_phase_x = (11 - x) * 0.05
            dir_phase_y = (11 - y) * 0.01
        elif d == 0:
            dir_phase_x = (11 - x) * 0.01
            dir_phase_y = (11 - y) * 0.05
        hue = int((phase_offset + dir_phase_x + dir_phase_y) * 255) % 255
        sat = 255
        val = 255
        r, g, b = self.hsv_to_rgb(hue, sat, val)
        return [r, g, b]

    def get_sensor_amplitude(self, sensor_id: int, t: int) -> int:
        offset = 5 * sensor_id
        scalar = 50
        amplitude = math.sin(t / scalar + offset) / 2 + 0.5
        scaled_amplitude = 100 * amplitude
        return int(scaled_amplitude)

    @staticmethod
    def hsv_to_rgb(hi: int, si: int, vi: int) -> tuple[int, int, int]:
        h = hi * 360.0 / 255.0
        s = si / 255.0
        v = vi / 255.0

        if s == 0.0:
            r = g = b = int(v * 255)
            return r, g, b

        i = int(h / 60.0) % 6
        f = (h / 60.0) - i
        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))

        if i == 0:
            r, g, b = v, t, p
        elif i == 1:
            r, g, b = q, v, p
        elif i == 2:
            r, g, b = p, v, t
        elif i == 3:
            r, g, b = p, q, v
        elif i == 4:
            r, g, b = t, p, v
        else:
            r, g, b = v, p, q
        return int(r * 255), int(g * 255), int(b * 255)
