import PySide6.QtCore as QtCore
import PySide6.QtGui as QtGui
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

    def get_name(self) -> tuple[bool, str]:
        if self.exec_() == QtWidgets.QDialog.DialogCode.Accepted:
            if name := self.name_input.text():
                return (True, name)
        return (False, "")


class KeyEntryDialog(QtWidgets.QDialog):
    """Dialog to enter keys for a user profile."""

    DIALOG_TITLE = "Enter key presses for each panel"
    ACCEPT_STR = "OK"

    def __init__(self):
        super(KeyEntryDialog, self).__init__()
        self.setWindowTitle(self.DIALOG_TITLE)

        self.key_inputs = [QtWidgets.QLineEdit() for _ in range(4)]
        accept = QtWidgets.QPushButton(self.ACCEPT_STR)
        accept.clicked.connect(self.accept)

        labels = ["Left", "Down", "Up", "Right"]
        regex = QtCore.QRegularExpression("[a-z-A-Z_]+]")
        validator = QtGui.QRegularExpressionValidator(regex)

        layout = QtWidgets.QVBoxLayout()
        for label, key_input in zip(labels, self.key_inputs):
            key_input.setMaxLength(1)
            key_input.setValidator(validator)
            key_layout = QtWidgets.QHBoxLayout()
            key_layout.addWidget(QtWidgets.QLabel(label))
            key_layout.addWidget(key_input)
            key_widget = QtWidgets.QWidget()
            key_widget.setLayout(key_layout)
            layout.addWidget(key_widget)
        layout.addWidget(accept)
        self.setLayout(layout)

    def get_keys(self) -> tuple[bool, list[str]]:
        if self.exec_() == QtWidgets.QDialog.DialogCode.Accepted:
            keys = []
            for key_input in self.key_inputs:
                keys.append(key_input.text())
            if len(keys) <= len(set(keys)):
                return (True, keys)
        return (False, [])


class ProfileWidget(QtWidgets.QWidget):
    """Widget to manage profile for a dance pad session."""

    NEW_ICON = QtWidgets.QStyle.StandardPixmap.SP_FileDialogNewFolder
    SAVE_ICON = QtWidgets.QStyle.StandardPixmap.SP_DialogSaveButton
    REMOVE_ICON = QtWidgets.QStyle.StandardPixmap.SP_DialogDiscardButton
    RENAME_ICON = QtWidgets.QStyle.StandardPixmap.SP_FileDialogDetailedView
    KEYS_ICON = QtWidgets.QStyle.StandardPixmap.SP_FileDialogListView

    LABEL_STR = "Profile:"

    DROP_H_POLICY = QtWidgets.QSizePolicy.Policy.Expanding
    DROP_V_POLICY = QtWidgets.QSizePolicy.Policy.Preferred

    LAYOUT_PADDING = (1, 1, 1, 1)

    NEW_CLICKED = QtCore.Signal()
    REMOVE_CLICKED = QtCore.Signal()
    RENAME_CLICKED = QtCore.Signal()
    SAVE_CLICKED = QtCore.Signal()
    DROPDOWN_ACTIVATED = QtCore.Signal(str)
    KEYS_CLICKED = QtCore.Signal()

    def __init__(self):
        super(ProfileWidget, self).__init__()

        self._label = QtWidgets.QLabel(self.LABEL_STR)
        self._new = self._create_tool_button(self.NEW_ICON)
        self._save = self._create_tool_button(self.SAVE_ICON)
        self._remove = self._create_tool_button(self.REMOVE_ICON)
        self._rename = self._create_tool_button(self.RENAME_ICON)
        self._keys = self._create_tool_button(self.KEYS_ICON)

        self._dropdown = QtWidgets.QComboBox()
        self._dropdown.setSizePolicy(self.DROP_H_POLICY, self.DROP_V_POLICY)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self._label)
        layout.addWidget(self._dropdown)
        layout.addWidget(self._new)
        layout.addWidget(self._rename)
        layout.addWidget(self._save)
        layout.addWidget(self._remove)
        layout.addWidget(self._keys)
        layout.setContentsMargins(*self.LAYOUT_PADDING)
        self.setLayout(layout)

        self._new.clicked.connect(self.NEW_CLICKED.emit)
        self._save.clicked.connect(self.SAVE_CLICKED.emit)
        self._remove.clicked.connect(self.REMOVE_CLICKED.emit)
        self._rename.clicked.connect(self.RENAME_CLICKED.emit)
        self._dropdown.activated.connect(self.DROPDOWN_ACTIVATED.emit)
        self._keys.clicked.connect(self.KEYS_CLICKED.emit)

    def _create_tool_button(
        self, icon: QtWidgets.QStyle.StandardPixmap
    ) -> QtWidgets.QToolButton:
        button = QtWidgets.QToolButton()
        button.setIcon(self.style().standardIcon(icon))
        return button

    def add_dropdown_item(self, item: str) -> None:
        self._dropdown.addItem(item)

    def remove_dropdown_item(self, item: str) -> None:
        self._dropdown.removeItem(self._dropdown.findText(item))

    def set_dropdown_state(self, active: bool) -> None:
        self._dropdown.setEnabled(active)

    def set_dropdown_items(self, items: list[str] | None = None) -> None:
        if not items:
            return
        self._dropdown.clear()
        self._dropdown.addItems(items)

    def get_num_dropdown_items(self) -> int:
        return self._dropdown.count()

    def get_dropdown_id(self) -> int:
        return self._dropdown.currentIndex()

    def set_dropdown_id(self, id: int) -> None:
        self._dropdown.setCurrentIndex(id)

    def set_dropdown_by_text(self, name: str) -> None:
        self._dropdown.setCurrentIndex(self._dropdown.findText(name))

    def rename_dropdown_item(self, names: tuple[str, str]) -> None:
        self._dropdown.setItemText(self._dropdown.findText(names[0]), names[1])

    def set_save_button(self, active: bool) -> None:
        self._save.setEnabled(active)

    def set_rename_button(self, active: bool) -> None:
        self._rename.setEnabled(active)

    def set_remove_button(self, active: bool) -> None:
        self._remove.setEnabled(active)

    def get_profile_name(self) -> tuple[bool, str]:
        return ProfileNameDialog().get_name()

    def get_keys(self) -> tuple[bool, list[str], str]:
        return (*KeyEntryDialog().get_keys(), self.get_pad_name())

    def get_pad_name(self) -> str:
        return self._dropdown.currentText()

    def set_new_button(self, active: bool) -> None:
        self._new.setEnabled(active)
