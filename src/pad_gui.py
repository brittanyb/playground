import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets
import qdarktheme
import sys

from pad_widget_controller import PadWidgetController
from pad_widget_view import PadWidgetView
from pad_model import PadModel
from test_data_generator import TestPadWidget


class PadConnection(QtWidgets.QWidget):
    def __init__(self):
        super(PadConnection, self).__init__()
        pad_refresh = QtWidgets.QToolButton()
        refresh_icon = QtWidgets.QStyle.StandardPixmap.SP_BrowserReload
        pad_refresh.setIcon(self.style().standardIcon(refresh_icon))
        pad_connection = QtWidgets.QToolButton()
        play_icon = QtWidgets.QStyle.StandardPixmap.SP_MediaPlay
        pad_connection.setIcon(self.style().standardIcon(play_icon))
        pad_dropdown = QtWidgets.QComboBox()
        pad_dropdown.setPlaceholderText("Brittany's Dance Pad")
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(pad_refresh)
        layout.addWidget(pad_connection)
        layout.addWidget(pad_dropdown)
        layout.setContentsMargins(1, 1, 1, 1)
        self.setLayout(layout)

    def refresh_pads(self):
        pass

    def toggle_pad_connection(self):
        pass

    def update_pad_list(self):
        pass


class MainWidget(QtWidgets.QWidget):
    def __init__(self):
        super(MainWidget, self).__init__()
        pad_connection = PadConnection()
        self.pad_model = PadModel()
        self.pad_view = PadWidgetView()
        self.pad_controller = PadWidgetController(
            self.pad_model, self.pad_view
        )
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(pad_connection)
        layout.addWidget(self.pad_controller)
        self.setLayout(layout)
        self.tester = TestPadWidget(self.pad_model, self.pad_controller)


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
