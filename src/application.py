import sys

import PySide6.QtCore as QtCore
import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets
import qdarktheme

from data_process import DataProcess
from gui_thread import GUIThread
from gui_widgets import Widgets
from profiler import Profiler


class MainWidget(QtWidgets.QWidget):
    """Central widget containing all Pad GUI widgets."""

    STYLESHEET = f"QSplitter::handle {{background-color: transparent;}}"

    def __init__(self):
        super(MainWidget, self).__init__()
        widgets = Widgets()
        self.update_thread = GUIThread(widgets)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setStyleSheet(self.STYLESHEET)
        splitter.addWidget(widgets.connection_widget)
        splitter.addWidget(widgets.profile_widget)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(splitter)
        layout.addWidget(widgets.pad_widget)
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
        self.widget.update_thread.terminate()
        event.accept()


class MainApplication(QtWidgets.QApplication):
    """Application entry point for Pad GUI."""

    FULL_WHITE = (255, 255, 255)
    REFLEX_PURPLE = {"primary": "#ad02ff"}

    ICON_PATH = "../assets/favicon.ico"

    def __init__(self):
        super(MainApplication, self).__init__(sys.argv)
        self.set_opengl_doublebuffering()
        self.set_application_theme()
        self.window = MainWindow()
        self.setup_interface()

    def setup_interface(self) -> None:
        self._data_proc = DataProcess()
        self.window.widget.update_thread.tx_queue = self._data_proc.rx_queue
        self.window.widget.update_thread.rx_queue = self._data_proc.tx_queue
        self._data_proc.start()
        self.window.widget.update_thread.start()
        self.aboutToQuit.connect(self.cleanup)

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
        palette.setColor(window_text, QtGui.QColor(*self.FULL_WHITE))
        self.setPalette(palette)

    def cleanup(self) -> None:
        self._data_proc.terminate()
        self._data_proc.join()
        self.quit()


if __name__ == "__main__":
    Profiler(5, 'gui.txt')
    app = MainApplication()
    app.exec()
