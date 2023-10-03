import PySide6.QtWidgets as QtWidgets

from profile_controller import ProfileController
from pad_model import PadModel


class ProfileWidget(QtWidgets.QWidget):
    """Widget to manage profile for a dance pad session."""

    def __init__(self, controller: ProfileController, model: PadModel):
        super(ProfileWidget, self).__init__()
        self._controller = controller
        self._model = model
        self._label = QtWidgets.QLabel("Profile:")
        self._new = QtWidgets.QToolButton()
        new_icon = QtWidgets.QStyle.StandardPixmap.SP_FileDialogNewFolder
        self._new.setIcon(self.style().standardIcon(new_icon))
        self._new.clicked.connect(self._create_new_profile)
        self._save = QtWidgets.QToolButton()
        save_icon = QtWidgets.QStyle.StandardPixmap.SP_DialogSaveButton
        self._save.setIcon(self.style().standardIcon(save_icon))
        self._save.clicked.connect(self._save_profile)
        self._rename = QtWidgets.QToolButton()
        rename_icon = QtWidgets.QStyle.StandardPixmap.SP_FileDialogDetailedView
        self._rename.setIcon(self.style().standardIcon(rename_icon))
        self._rename.clicked.connect(self._rename_profile)
        self._remove = QtWidgets.QToolButton()
        remove_icon = QtWidgets.QStyle.StandardPixmap.SP_DialogDiscardButton
        self._remove.setIcon(self.style().standardIcon(remove_icon))
        self._remove.clicked.connect(self._remove_profile)
        self._dropdown = QtWidgets.QComboBox()
        self._dropdown.activated.connect(self._load_profile)
        expand = QtWidgets.QSizePolicy.Policy.Expanding
        prefer = QtWidgets.QSizePolicy.Policy.Preferred
        self._dropdown.setSizePolicy(expand, prefer)
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self._label)
        layout.addWidget(self._dropdown)
        layout.addWidget(self._new)
        layout.addWidget(self._rename)
        layout.addWidget(self._save)
        layout.addWidget(self._remove)
        layout.setContentsMargins(1, 1, 1, 1)
        self.setLayout(layout)
        self.set_dropdown_contents()
        if self._dropdown.count() == 0:
            self._create_new_profile()
        self._load_profile()

    def set_dropdown_contents(self) -> None:
        self._dropdown.clear()
        for profile_name in sorted(self._controller.profile_names):
            self._dropdown.addItem(profile_name)
        if self._dropdown.count() == 0:
            self._dropdown.setDisabled(True)

    def set_widget_states(self) -> None:
        if self._dropdown.count() == 0:
            self._dropdown.setDisabled(True)
            self._remove.setDisabled(True)
            self._save.setDisabled(True)
            self._rename.setDisabled(True)
            return
        self._dropdown.setEnabled(True)
        self._remove.setEnabled(True)
        self._rename.setEnabled(True)
        self.set_save_state()

    def set_save_state(self) -> None:
        if self._controller.saved_data != self._model.profile_data:
            self._save.setEnabled(True)
        else:
            self._save.setDisabled(True)

    def _save_profile(self) -> None:
        name = self._dropdown.currentText()
        self._controller.save_user_profile(name)
        self.set_save_state()

    def _load_profile(self) -> None:
        name = self._dropdown.currentText()
        self._controller.load_user_profile(name)
        self.set_widget_states()

    def _rename_profile(self) -> None:
        if not self._dropdown.isEnabled():
            return
        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle("Enter new profile name")
        layout = QtWidgets.QVBoxLayout()
        name_input = QtWidgets.QLineEdit()
        accept = QtWidgets.QPushButton("OK")
        accept.clicked.connect(dialog.accept)
        layout.addWidget(name_input)
        layout.addWidget(accept)
        dialog.setLayout(layout)
        if dialog.exec_() == QtWidgets.QDialog.DialogCode.Accepted:
            new_name = name_input.text()
            old_name = self._dropdown.currentText()
            self._controller.rename_user_profile(old_name, new_name)
            self.set_dropdown_contents()
            self.set_widget_states()
            self._dropdown.setCurrentIndex(self._dropdown.findText(new_name))

    def _remove_profile(self) -> None:
        name = self._dropdown.currentText()
        index = self._dropdown.currentIndex()
        self._controller.remove_user_profile(name)
        self._dropdown.removeItem(index)
        self.set_widget_states()
        if index > 0:
            self._dropdown.setCurrentIndex(index - 1)
            self._load_profile()
        elif self._dropdown.count() == 0:
            self._create_new_profile()
            self._dropdown.setCurrentIndex(0)
            self.set_dropdown_contents()
            self.set_widget_states()
        else:
            self._dropdown.setCurrentIndex(0)
            self._load_profile()

    def _create_new_profile(self) -> None:
        name = self._controller.create_new_profile()
        self._dropdown.addItem(name)
        self.set_dropdown_contents()
        self.set_widget_states()
        self._dropdown.setCurrentIndex(self._dropdown.findText(name))
