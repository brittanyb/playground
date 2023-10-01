import sys

import PySide6.QtCore as QtCore
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

    def __init__(
        self, pad_model: PadModel, profile_controller: ProfileController
    ):
        super(MainWidget, self).__init__()
        self.pad_connection = ConnectionWidget()
        self.pad_profile = ProfileWidget(profile_controller)
        self.pad_display = PadWidget(pad_model)
        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        style = f"QSplitter::handle {{background-color: transparent;}}"
        splitter.setStyleSheet(style)
        splitter.addWidget(self.pad_connection)
        splitter.addWidget(self.pad_profile)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(splitter)
        layout.addWidget(self.pad_display)
        self.setLayout(layout)


class MainWindow(QtWidgets.QMainWindow):
    """Main window for Pad GUI."""

    def __init__(
            self, pad_model: PadModel, profile_controller: ProfileController
    ):
        super(MainWindow, self).__init__()
        widget = MainWidget(pad_model, profile_controller)
        self.setWindowTitle("RE:Flex Dance - Playground")
        self.setCentralWidget(widget)
        self.setFixedSize(widget.width(), widget.height())


class MainApplication(QtWidgets.QApplication):
    """Application entry point for Pad GUI."""

    def __init__(self):
        super(MainApplication, self).__init__(sys.argv)
        self.set_opengl_doublebuffering()
        self.set_application_theme()
        self.set_shared_resources()
        self.window = MainWindow(self.pad_model, self.profile_controller)
        self.window.show()

    @staticmethod
    def set_opengl_doublebuffering() -> None:
        format = QtGui.QSurfaceFormat()
        format.setSwapInterval(1)
        format.setSwapBehavior(QtGui.QSurfaceFormat.SwapBehavior.DoubleBuffer)
        QtGui.QSurfaceFormat.setDefaultFormat(format)

    def set_application_theme(self) -> None:
        self.setWindowIcon(QtGui.QIcon("../assets/favicon.ico"))
        qdarktheme.setup_theme(custom_colors={"primary": "#ad02ff"})
        palette = self.palette()
        window_text = QtGui.QPalette.ColorRole.WindowText
        palette.setColor(window_text, QtGui.QColor(255, 255, 255))
        self.setPalette(palette)

    def set_shared_resources(self) -> None:
        self.pad_model = PadModel()
        self.profile_controller = ProfileController()


if __name__ == "__main__":
    app = MainApplication()
    app.exec()
