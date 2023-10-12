import multiprocessing
import sys

import PySide6.QtCore as QtCore
import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets
import qdarktheme

from connection_widget import ConnectionWidget
from gui_event_manager import GUIEventManager
from interface_process import InterfaceProcess
from profile_widget import ProfileWidget
from pad_widget import PadWidget


class MainWidget(QtWidgets.QWidget):
    """Central widget containing all Pad GUI widgets."""

    STYLESHEET = f"QSplitter::handle {{background-color: transparent;}}"

    def __init__(self):
        super(MainWidget, self).__init__()
        self._pad_connection = ConnectionWidget()
        self._pad_profile = ProfileWidget()
        self._pad_widget = PadWidget()
        self.event_manager = GUIEventManager(
            self._pad_connection, self._pad_widget, self._pad_profile
        )

        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setStyleSheet(self.STYLESHEET)
        splitter.addWidget(self._pad_connection)
        splitter.addWidget(self._pad_profile)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(splitter)
        layout.addWidget(self._pad_widget)
        self.setLayout(layout)


class MainWindow(QtWidgets.QMainWindow):
    """Main window for Pad GUI."""

    TITLE = "RE:Flex Dance - Playground"

    def __init__(self):
        super(MainWindow, self).__init__()
        self.widget = MainWidget()
        self.setWindowTitle(self.TITLE)
        self.setCentralWidget(self.widget)
        max_button = QtCore.Qt.WindowType.WindowMaximizeButtonHint
        self.setWindowFlag(max_button, False)
        self.show()
        self.setFixedSize(self.width(), self.height())

    def closeEvent(self, event: QtCore.QEvent) -> None:
        self.widget.event_manager.terminate()
        event.accept()


class MainApplication(QtWidgets.QApplication):
    """Application entry point for Pad GUI."""

    FULL_BLACK = (255, 255, 255)
    REFLEX_PURPLE = {"primary": "#ad02ff"}

    ICON_PATH = "../assets/favicon.ico"

    def __init__(self):
        super(MainApplication, self).__init__(sys.argv)
        self.set_opengl_doublebuffering()
        self.set_application_theme()
        self.window = MainWindow()
        self.setup_interface()

    def setup_interface(self) -> None:
        self.interface_process = InterfaceProcess()
        self.window.widget.event_manager.queue = self.interface_process.queue
        self.interface_process.start()
        self.window.widget.event_manager.start()

    @staticmethod
    def set_opengl_doublebuffering() -> None:
        format = QtGui.QSurfaceFormat()
        format.setSwapInterval(1)
        format.setSwapBehavior(QtGui.QSurfaceFormat.SwapBehavior.DoubleBuffer)
        QtGui.QSurfaceFormat.setDefaultFormat(format)

    def set_application_theme(self) -> None:
        self.setWindowIcon(QtGui.QIcon(self.ICON_PATH))
        qdarktheme.setup_theme(custom_colors=dict(self.REFLEX_PURPLE))
        palette = self.palette()
        window_text = QtGui.QPalette.ColorRole.WindowText
        palette.setColor(window_text, QtGui.QColor(*self.FULL_BLACK))
        self.setPalette(palette)


if __name__ == "__main__":
    app = MainApplication()
    app.exec()
