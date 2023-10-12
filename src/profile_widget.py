import PySide6.QtWidgets as QtWidgets


class ProfileNameDialog(QtWidgets.QDialog):
    def __init__(self):
        super(ProfileNameDialog, self).__init__()
        self.setWindowTitle("Enter new profile name")

        self.name_input = QtWidgets.QLineEdit()
        accept = QtWidgets.QPushButton("OK")
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

    def __init__(self):
        super(ProfileWidget, self).__init__()

        self._label = QtWidgets.QLabel("Profile:")
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

    def _create_tool_button(
        self, icon: QtWidgets.QStyle.StandardPixmap
    ) -> QtWidgets.QToolButton:
        button = QtWidgets.QToolButton()
        button.setIcon(self.style().standardIcon(icon))
        return button

    def add_dropdown_item(self, item: str) -> None:
        self._dropdown.addItem(item)

    def set_dropdown_items(self, items: list[str] | None = None) -> None:
        if not items:
            return
        self._dropdown.clear()
        self._dropdown.addItems(items)

    def set_dropdown_id(self, name: str) -> None:
        self._dropdown.setCurrentIndex(self._dropdown.findText(name))

    def set_widget_state(self) -> None:
        if self._dropdown.count() == 0:
            self._dropdown.setDisabled(True)
            self._remove.setDisabled(True)
            self._rename.setDisabled(True)
            self._save.setDisabled(True)
            return
        self._dropdown.setEnabled(True)
        self._remove.setEnabled(True)
        self._rename.setEnabled(True)

    def set_save_button(self, profile_unsaved: bool) -> None:
        if profile_unsaved:
            self._save.setEnabled(True)
        else:
            self._save.setDisabled(True)

    def get_profile_name(self) -> str | None:
        if not self._dropdown.isEnabled():
            return
        dialog = ProfileNameDialog()
        return dialog.get_name()

    @property
    def selected_pad_name(self) -> str:
        return self._dropdown.currentText()
