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
from reflex_controller import ReflexController
from test_data_generator import TestPadWidget


class MainWidget(QtWidgets.QWidget):
    """Central widget containing all Pad GUI widgets."""

    def __init__(
        self, pad_model: PadModel, profile_controller: ProfileController,
        pad_controller: ReflexController
    ):
        super(MainWidget, self).__init__()
        self.pad_connection = ConnectionWidget(pad_controller)
        self.pad_profile = ProfileWidget(profile_controller, pad_model)
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
        self.test_widget = TestPadWidget(pad_model, self.pad_display)


class MainWindow(QtWidgets.QMainWindow):
    """Main window for Pad GUI."""

    def __init__(
            self, pad_model: PadModel, profile_controller: ProfileController,
            pad_controller: ReflexController
    ):
        super(MainWindow, self).__init__()
        self.widget = MainWidget(pad_model, profile_controller, pad_controller)
        self.setWindowTitle("RE:Flex Dance - Playground")
        self.setCentralWidget(self.widget)
        max_button = QtCore.Qt.WindowType.WindowMaximizeButtonHint
        self.setWindowFlag(max_button, False)
        self.show()
        self.setFixedSize(self.width(), self.height())


class MainApplication(QtWidgets.QApplication):
    """Application entry point for Pad GUI."""

    def __init__(self):
        super(MainApplication, self).__init__(sys.argv)
        self.set_opengl_doublebuffering()
        self.set_application_theme()
        self.set_shared_resources()
        self.window = MainWindow(
            self.pad_model, self.profile_controller, self.pad_controller
        )
        model_update = self.window.widget.pad_display.update_event
        set_widget = self.window.widget.pad_profile.set_save_state
        model_update.connect(set_widget)

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
        self.pad_controller = ReflexController()
        self.profile_controller = ProfileController(self.pad_model)


if __name__ == "__main__":
    app = MainApplication()
    app.exec()
