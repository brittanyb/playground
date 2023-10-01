import sys

import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets
import qdarktheme

from connection_widget import ConnectionWidget
from profile_widget import ProfileWidget
from profile_controller import ProfileController
from pad_widget import PadWidget
from pad_model import PadModel


class MainWidget(QtWidgets.QWidget):
    """Central widget containing all Pad GUI widgets."""

    def __init__(self):
        super(MainWidget, self).__init__()
        pad_connection = ConnectionWidget()
        self.pad_model = PadModel()
        self.pad_widget = PadWidget(self.pad_model)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(pad_connection)
        layout.addWidget(self.pad_widget)
        self.setLayout(layout)


class MainWindow(QtWidgets.QMainWindow):
    """Main window for Pad GUI."""

    def __init__(self):
        super(MainWindow, self).__init__()
        widget = MainWidget()
        self.setWindowTitle("RE:Flex Dance - Playground")
        self.setCentralWidget(widget)
        self.setFixedSize(widget.width(), widget.height())


class MainApplication(QtWidgets.QApplication):
    """Application entry point for Pad GUI."""

    def __init__(self):
        super(MainApplication, self).__init__(sys.argv)
        self.set_opengl_doublebuffering()
        self.set_application_theme()
        self.window = MainWindow()
        self.window.show()

    @staticmethod
    def set_opengl_doublebuffering():
        format = QtGui.QSurfaceFormat()
        format.setSwapInterval(1)
        format.setSwapBehavior(QtGui.QSurfaceFormat.SwapBehavior.DoubleBuffer)
        QtGui.QSurfaceFormat.setDefaultFormat(format)

    def set_application_theme(self):
        self.setWindowIcon(QtGui.QIcon("../assets/favicon.ico"))
        qdarktheme.setup_theme(custom_colors={"primary": "#ad02ff"})
        palette = self.palette()
        window_text = QtGui.QPalette.ColorRole.WindowText
        palette.setColor(window_text, QtGui.QColor(255, 255, 255))
        self.setPalette(palette)


if __name__ == "__main__":
    app = MainApplication()
    app.exec()
