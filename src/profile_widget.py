import PySide6.QtWidgets as QtWidgets

from profile_controller import ProfileController


class ProfileWidget(QtWidgets.QWidget):
    """Widget to manage profile for a dance pad session."""

    def __init__(self, profile_controller):
        super(ProfileWidget, self).__init__()
        self._label = QtWidgets.QLabel("Profile: ")
        self._new = QtWidgets.QToolButton()
        self._save = QtWidgets.QToolButton()
        self._dropdown = QtWidgets.QComboBox()
        expand = QtWidgets.QSizePolicy.Policy.Expanding
        prefer = QtWidgets.QSizePolicy.Policy.Preferred
        self._dropdown.setSizePolicy(expand, prefer)
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self._label)
        layout.addWidget(self._dropdown)
        layout.addWidget(self._new)
        layout.addWidget(self._save)
        layout.setContentsMargins(1, 1, 1, 1)
        self.setLayout(layout)
        self.set_widget_states()

    def _set_save(self) -> None:
        pass

    def _set_dropdown(self) -> None:
        pass

    def _set_new(self) -> None:
        pass

    def set_widget_states(self) -> None:
        self._set_new()
        self._set_save()
        self._set_dropdown()
