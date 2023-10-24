import PySide6.QtCore as QtCore
import PySide6.QtWidgets as QtWidgets


class ProfileNameDialog(QtWidgets.QDialog):
    """Dialog to re-name a user profile."""

    DIALOG_TITLE = "Enter new profile name"
    ACCEPT_STR = "OK"

    def __init__(self):
        super(ProfileNameDialog, self).__init__()
        self.setWindowTitle(self.DIALOG_TITLE)

        self.name_input = QtWidgets.QLineEdit()
        accept = QtWidgets.QPushButton(self.ACCEPT_STR)
        accept.clicked.connect(self.accept)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.name_input)
        layout.addWidget(accept)
        self.setLayout(layout)

    def get_name(self) -> str | None:
        if self.exec_() == QtWidgets.QDialog.DialogCode.Accepted:
            return self.name_input.text()


class ProfileWidget(QtWidgets.QWidget):
    """Widget to manage profile for a dance pad session."""

    NEW_ICON = QtWidgets.QStyle.StandardPixmap.SP_FileDialogNewFolder
    SAVE_ICON = QtWidgets.QStyle.StandardPixmap.SP_DialogSaveButton
    REMOVE_ICON = QtWidgets.QStyle.StandardPixmap.SP_DialogDiscardButton
    RENAME_ICON = QtWidgets.QStyle.StandardPixmap.SP_FileDialogDetailedView

    LABEL_STR = "Profile:"

    DROP_H_POLICY = QtWidgets.QSizePolicy.Policy.Expanding
    DROP_V_POLICY = QtWidgets.QSizePolicy.Policy.Preferred

    LAYOUT_PADDING = (1, 1, 1, 1)

    NEW_CLICKED = QtCore.Signal()
    REMOVE_CLICKED = QtCore.Signal()
    RENAME_CLICKED = QtCore.Signal()
    SAVE_CLICKED = QtCore.Signal()
    DROPDOWN_ACTIVATED = QtCore.Signal(str)

    def __init__(self):
        super(ProfileWidget, self).__init__()

        self._label = QtWidgets.QLabel(self.LABEL_STR)
        self._new = self._create_tool_button(self.NEW_ICON)
        self._save = self._create_tool_button(self.SAVE_ICON)
        self._remove = self._create_tool_button(self.REMOVE_ICON)
        self._rename = self._create_tool_button(self.RENAME_ICON)

        self._dropdown = QtWidgets.QComboBox()
        self._dropdown.setSizePolicy(self.DROP_H_POLICY, self.DROP_V_POLICY)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self._label)
        layout.addWidget(self._dropdown)
        layout.addWidget(self._new)
        layout.addWidget(self._rename)
        layout.addWidget(self._save)
        layout.addWidget(self._remove)
        layout.setContentsMargins(*self.LAYOUT_PADDING)
        self.setLayout(layout)

        self._new.clicked.connect(self.NEW_CLICKED.emit)
        self._save.clicked.connect(self.SAVE_CLICKED.emit)
        self._remove.clicked.connect(self.REMOVE_CLICKED.emit)
        self._rename.clicked.connect(self.RENAME_CLICKED.emit)
        self._dropdown.activated.connect(self.DROPDOWN_ACTIVATED.emit)

    def _create_tool_button(
        self, icon: QtWidgets.QStyle.StandardPixmap
    ) -> QtWidgets.QToolButton:
        button = QtWidgets.QToolButton()
        button.setIcon(self.style().standardIcon(icon))
        button.setEnabled(False)
        return button

    def add_dropdown_item(self, item: str) -> None:
        self._dropdown.addItem(item)

    def set_dropdown_state(self, active: bool) -> None:
        self._dropdown.setEnabled(active)

    def set_dropdown_items(self, items: list[str] | None = None) -> None:
        if not items:
            return
        self._dropdown.clear()
        self._dropdown.addItems(items)

    def set_dropdown_id(self, name: str) -> None:
        self._dropdown.setCurrentIndex(self._dropdown.findText(name))

    def set_save_button(self, active: bool) -> None:
        self._save.setEnabled(active)

    def get_profile_name(self) -> str | None:
        if not self._dropdown.isEnabled():
            return
        return ProfileNameDialog().get_name()

    def get_pad_name(self) -> str:
        return self._dropdown.currentText()
