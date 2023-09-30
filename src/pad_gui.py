import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets
import qdarktheme
import sys

from connection_widget import ConnectionWidget
from pad_widget_controller import PadWidgetController
from pad_widget_view import PadWidgetView
from pad_model import PadModel
from test_data_generator import TestPadWidget


class MainWidget(QtWidgets.QWidget):
    def __init__(self):
        super(MainWidget, self).__init__()
        pad_connection = ConnectionWidget()
        self.pad_model = PadModel()
        self.pad_view = PadWidgetView()
        self.pad_controller = PadWidgetController(
            self.pad_model, self.pad_view
        )
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(pad_connection)
        layout.addWidget(self.pad_controller)
        self.setLayout(layout)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setFixedSize(858, 895)
        self.setWindowTitle("RE:Flex Dance - Playground")
        self.setCentralWidget(MainWidget())


class MainApplication(QtWidgets.QApplication):
    def __init__(self):
        super(MainApplication, self).__init__(sys.argv)
        self.set_opengl_doublebuffering()
        self.setWindowIcon(QtGui.QIcon("../assets/favicon.ico"))
        qdarktheme.setup_theme(custom_colors={"primary": "#ad02ff"})
        palette = self.palette()
        window_text = QtGui.QPalette.ColorRole.WindowText
        palette.setColor(window_text, QtGui.QColor(255, 255, 255))
        self.setPalette(palette)
        self.window = MainWindow()
        self.window.show()

    @staticmethod
    def set_opengl_doublebuffering():
        format = QtGui.QSurfaceFormat()
        format.setSwapInterval(1)
        format.setSwapBehavior(QtGui.QSurfaceFormat.SwapBehavior.DoubleBuffer)
        QtGui.QSurfaceFormat.setDefaultFormat(format)


if __name__ == "__main__":
    app = MainApplication()
    app.exec()
