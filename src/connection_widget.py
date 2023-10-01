import PySide6.QtWidgets as QtWidgets

from reflex_controller import ReflexController


class ConnectionWidget(QtWidgets.QWidget):
    """Widget to manage an open connection to a dance pad."""

    def __init__(self):
        super(ConnectionWidget, self).__init__()
        self._controller = ReflexController()
        self._active = False
        refresh_icon = QtWidgets.QStyle.StandardPixmap.SP_BrowserReload
        self._refresh = QtWidgets.QToolButton()
        self._refresh.setIcon(self.style().standardIcon(refresh_icon))
        self._refresh.clicked.connect(self.refresh_pads)
        self._connect = QtWidgets.QToolButton()
        self._connect.clicked.connect(self.toggle_pad_connection)
        self._dropdown = QtWidgets.QComboBox()
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self._refresh)
        layout.addWidget(self._connect)
        layout.addWidget(self._dropdown)
        layout.setContentsMargins(1, 1, 1, 1)
        self.setLayout(layout)
        self.refresh_pads()
        self.set_widget_states()

    def _set_connect_button(self) -> None:
        if self._active:
            icon = QtWidgets.QStyle.StandardPixmap.SP_MediaStop
        else:
            icon = QtWidgets.QStyle.StandardPixmap.SP_MediaPlay
        self._connect.setIcon(self.style().standardIcon(icon))
        self._connect.update()
        if not len(self._controller.all_pads):
            self._connect.setDisabled(True)
            return
        self._connect.setEnabled(True)

    def _set_dropdown(self) -> None:
        if self._active:
            self._dropdown.setDisabled(True)
            return
        for _ in range(self._dropdown.count()):
            self._dropdown.removeItem(0)
        serials = [s for s in self._controller.all_pads if isinstance(s, str)]
        if len(serials):
            for serial in sorted(serials):
                if serial:
                    self._dropdown.addItem(serial)
        self._dropdown.setEnabled(True)

    def _set_refresh(self) -> None:
        if self._active:
            self._refresh.setDisabled(True)
            return
        self._refresh.setEnabled(True)

    def set_widget_states(self) -> None:
        self._set_connect_button()
        self._set_dropdown()
        self._set_refresh()

    def refresh_pads(self) -> None:
        self._controller.enumerate_pads()
        self.set_widget_states()

    def toggle_pad_connection(self) -> None:
        if self._active:
            if pad := self._controller.connected_pads[0]:
                self._controller.disconnect_pad(pad.serial)
                self._active = False
        else:
            serial = self._dropdown.itemText(self._dropdown.currentIndex())
            if self._controller.connect_pad(serial):
                self._active = True
        self.set_widget_states()
