import PySide6.QtWidgets as QtWidgets


class ConnectionWidget(QtWidgets.QWidget):
    """Widget to manage a single dance pad connection."""

    REFRESH_ICON = QtWidgets.QStyle.StandardPixmap.SP_BrowserReload
    CONNECT_PAD_ICON = QtWidgets.QStyle.StandardPixmap.SP_MediaPlay
    DISCONNECT_PAD_ICON = QtWidgets.QStyle.StandardPixmap.SP_MediaStop

    LABEL_STR = "Pad:"

    DROP_H_POLICY = QtWidgets.QSizePolicy.Policy.Expanding
    DROP_V_POLICY = QtWidgets.QSizePolicy.Policy.Preferred

    LABEL_PADDING = (0, 0, 0, 0)
    LAYOUT_PADDING = (1, 1, 1, 1)

    def __init__(self):
        super(ConnectionWidget, self).__init__()

        self._refresh = QtWidgets.QToolButton()
        self._set_toolbutton_icon(self._refresh, self.REFRESH_ICON)
        self._connect = QtWidgets.QToolButton()
        self._label = QtWidgets.QLabel(self.LABEL_STR)
        self._label.setContentsMargins(*self.LABEL_PADDING)
        self._dropdown = QtWidgets.QComboBox()
        self._dropdown.setSizePolicy(self.DROP_H_POLICY, self.DROP_V_POLICY)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self._label)
        layout.addWidget(self._dropdown)
        layout.addWidget(self._connect)
        layout.addWidget(self._refresh)
        layout.setContentsMargins(*self.LAYOUT_PADDING)
        self.setLayout(layout)

    def _set_toolbutton_icon(
        self, button: QtWidgets.QToolButton,
        icon: QtWidgets.QStyle.StandardPixmap
    ) -> None:
        button.setIcon(self.style().standardIcon(icon))
        button.update()

    def set_connect_button(self, active: bool, pads: bool) -> None:
        if active:
            self._set_toolbutton_icon(self._connect, self.DISCONNECT_PAD_ICON)
        else:
            self._set_toolbutton_icon(self._connect, self.CONNECT_PAD_ICON)
        if not pads:
            self._connect.setDisabled(True)
        else:
            self._connect.setEnabled(True)

    def set_dropdown(
        self, active: bool, items: list[str] | None = None
    ) -> None:
        pad_name = self._dropdown.currentText()
        self._dropdown.clear()
        if items:
            self._dropdown.addItems(items)
        if not active:
            self._dropdown.setDisabled(True)
        else:
            self._dropdown.setEnabled(True)
        if pad_name and (index := self._dropdown.findText(pad_name)):
            self._dropdown.setCurrentIndex(index)
        else:
            self._dropdown.setCurrentIndex(0)

    def set_refresh_button(self, active: bool) -> None:
        if active:
            self._refresh.setDisabled(True)
        else:
            self._refresh.setEnabled(True)

    @property
    def current_pad_serial(self) -> str:
        return self._dropdown.currentText()
