import PySide6.QtCore as QtCore
import PySide6.QtGui as QtGui
import PySide6.QtOpenGLWidgets as QtOpenGLWidgets

from pad_model import PadModel, PadEntry, Coord
from pad_widget_view import PadWidgetView


class PadWidget(QtOpenGLWidgets.QOpenGLWidget):
    """An animated widget displaying sensor and LED data."""

    FRAME_READY = QtCore.Signal()
    NEW_SENS_VALUE = QtCore.Signal()

    def __init__(self):
        super(PadWidget, self).__init__()
        self.setFixedSize(PadWidgetView.SIZE, PadWidgetView.SIZE)
        self.view = PadWidgetView()
        self.setMouseTracking(True)
        self._dragging = False
        self._last_mouse_y = None
        self._rect_coord = None
        self._button = None
        self._model = PadModel()

    def initializeGL(self) -> None:
        self.view.init_painting(self._model.get_model_data())

    def resizeGL(self, w: int, h: int) -> None:
        self.view.handle_resize_event(w, h)

    def paintGL(self) -> None:
        self.view.draw_widget()

    def update(self, frame_data: PadEntry) -> None:
        self.view.set_frame_data(frame_data)
        super().update()
        self.FRAME_READY.emit()

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
        self._mouse_y = m_y - self._last_mouse_y
        self._last_mouse_y = m_y
        self.NEW_SENS_VALUE.emit()

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if (self._rect_coord):
            self._dragging = True
            self._button = event.button()
            self._last_mouse_y = PadWidgetView.SIZE - event.y()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        self._dragging = False
        event.accept()

    def get_update_data(self) -> tuple[int, int, tuple[Coord, Coord]] | None:
        if self._rect_coord is None:
            return None
        if self._button == QtCore.Qt.MouseButton.LeftButton:
            update_id = 0
        elif self._button == QtCore.Qt.MouseButton.RightButton:
            update_id = 1
        else:
            update_id = 2
        return (update_id, self._mouse_y, self._rect_coord)
