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


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon("../assets/favicon.ico"))
    qdarktheme.setup_theme(custom_colors={"primary": "#ad02ff"})
    palette = app.palette()
    palette.setColor(QtGui.QPalette.ColorRole.WindowText,
                     QtGui.QColor(255, 255, 255))
    app.setPalette(palette)
    format = QtGui.QSurfaceFormat()
    format.setSwapInterval(1)
    format.setSwapBehavior(QtGui.QSurfaceFormat.SwapBehavior.DoubleBuffer)
    QtGui.QSurfaceFormat.setDefaultFormat(format)
    window = MainWindow()
    window.show()
    app.exec()
