import time

from pad_model import PadModel, Coord, Colour


class LEDDataGenerator:
    """Dummy data to test pad widget animations."""

    @staticmethod
    def panel_bases() -> dict[Coord, list[Coord]]:
        def rotate(grid: list[list[int]], num_rots: int) -> list[list[int]]:
            for _ in range(num_rots):
                grid = [list(reversed(row)) for row in zip(*grid)]
            return grid

        ARROW_BASE = [
            [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0],
            [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
        ]

        panel_bases = {}
        for coord in PadModel.PANELS.coords:
            if coord == (0, 1):
                num_rots = 3
            elif coord == (1, 0):
                num_rots = 2
            elif coord == (2, 1):
                num_rots = 1
            else:
                num_rots = 0
            base = rotate(ARROW_BASE, num_rots)
            coords = []
            for y, row in enumerate(base):
                for x, value in enumerate(row):
                    if value != 0:
                        coords.append((x, y))
            panel_bases[coord] = coords
        return panel_bases
    
    PANEL_BASES = panel_bases()

    def __init__(
        self, model: PadModel
    ):
        self._t = 0
        self._model = model
        self._att = 0.05
        self._dec = 0.1
        self._tim = {}

    def update_led_frame(self) -> None:
        self._t += 1
        self._current_data = self._model.get_model_data()
        for panel_coord, panel in self._current_data.panels.items():
            active_leds = self.PANEL_BASES[panel_coord]
            panel_value = self.get_panel_value(panel_coord)
            for led_coord, led in panel.leds.items():
                if led_coord in active_leds:
                    led.colour = self.get_led_colour(panel_coord, led_coord, panel_value)

    def get_led_colour(self, panel: Coord, led: Coord, value: float) -> Colour:
        phase_multiplier = 0.003
        phase_offset = self._t * phase_multiplier
        dir_phase_x = 0
        dir_phase_y = 0
        x = led[0]
        y = led[1]
        if panel == PadModel.PANELS.coords[1]:
            dir_phase_x = x * 0.01
            dir_phase_y = y * 0.05
        elif panel == PadModel.PANELS.coords[3]:
            dir_phase_x = x * 0.05
            dir_phase_y = y * 0.01
        elif panel == PadModel.PANELS.coords[2]:
            dir_phase_x = (11 - x) * 0.01
            dir_phase_y = (11 - y) * 0.05
        else:
            dir_phase_x = (11 - x) * 0.05
            dir_phase_y = (11 - y) * 0.01
        hue = int((phase_offset + dir_phase_x + dir_phase_y) * 255) % 255
        sat = 255
        val = int(255 * value)
        r, g, b = self.hsv_to_rgb(hue, sat, val)
        return (r, g, b)
    
    def get_panel_value(self, panel: Coord) -> float:
        current_time = time.time()
        if self._current_data.panels[panel].active:
            if panel not in self._tim or not self._tim[panel]['active']:
                self._tim[panel] = {'start': current_time, 'active': True}
            elapsed = current_time - self._tim[panel]['start']
            if elapsed < self._att:
                return elapsed / self._att
            return 1.0
        else:
            if panel not in self._tim:
                return 0.0
            if self._tim[panel].get('end', None) is None:
                self._tim[panel]['end'] = current_time
                self._tim[panel]['active'] = False
            elapsed = current_time - self._tim[panel]['end']
            if elapsed < self._dec:
                return 1.0 - (elapsed / self._dec)
            return 0.0

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
        return int(r * 75), int(g * 75), int(b * 75)
