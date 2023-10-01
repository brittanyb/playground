import PySide6.QtCore as QtCore
import PySide6.QtGui as QtGui
import PySide6.QtOpenGLWidgets as QtOpenGLWidgets

from pad_model import PadModel
from pad_widget_view import PadWidgetView


class PadWidget(QtOpenGLWidgets.QOpenGLWidget):
    """An animated widget displaying sensor and LED data."""

    def __init__(self, pad_model: PadModel):
        super(PadWidget, self).__init__()
        self.setFixedSize(PadWidgetView.SIZE, PadWidgetView.SIZE)
        self.model = pad_model
        self.view = PadWidgetView()
        self.setMouseTracking(True)
        self._dragging = False
        self._last_mouse_y = None
        self._rect_coord = None
        self._button = None

    def initializeGL(self) -> None:
        self.view.init_painting(self.model)

    def resizeGL(self, w: int, h: int) -> None:
        self.view.handle_resize_event(w, h)

    def paintGL(self) -> None:
        self.view.draw_widget()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        m_x = event.x()
        m_y = PadWidgetView.SIZE - event.y()
        if not self._dragging:
            self._rect_coord = self.view.mouse_in_threshold_rect(m_x, m_y)
        if (self._rect_coord):
            self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        else:
            self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
        if (
            not self._dragging or
            self._last_mouse_y is None or
            not self._rect_coord or
            self._button is None
        ):
            return
        panel = self.model.panel_at_coord(self._rect_coord[0])
        if not panel:
            return
        sensor = panel.sensor_at_coord(self._rect_coord[1])
        if not sensor:
            return
        mouse_diff = m_y - self._last_mouse_y
        if self._button == QtCore.Qt.MouseButton.LeftButton:
            sensor.threshold += mouse_diff
        elif self._button == QtCore.Qt.MouseButton.RightButton:
            sensor.hysteresis -= mouse_diff
        self._last_mouse_y = m_y

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if (self._rect_coord):
            self._dragging = True
            self._button = event.button()
            self._last_mouse_y = PadWidgetView.SIZE - event.y()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        self._dragging = False
