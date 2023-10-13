import multiprocessing.queues

import PySide6.QtCore as QtCore

from connection_widget import ConnectionWidget
from gui_event import GUIEvent
from gui_event_handler import GUIEventHandler
from interface_event import IFEvent
from pad_widget import PadWidget
from profile_widget import ProfileWidget


class GUIEventManager(QtCore.QThread):
    """Thread for GUI that handles event data TX/RX to interface process."""

    INIT_DATA_RECEIVED = QtCore.Signal(list)

    def __init__(
        self, connection_widget: ConnectionWidget, pad_widget: PadWidget,
        profile_widget: ProfileWidget
    ):
        super(GUIEventManager, self).__init__()
        self.daemon = True
        self._connection_widget = connection_widget
        self._pad_widget = pad_widget
        self._profile_widget = profile_widget
        self._rx_queue = None
        self._tx_queue = None
        self._event_handler = GUIEventHandler(
            connection_widget, pad_widget, profile_widget
        )

        self.create_widget_event_hooks()
        self.create_widget_update_hooks()

    def create_widget_event_hooks(self) -> None:
        widget_event_map = {
            self._connection_widget._refresh.clicked: GUIEvent.REFRESH,
            self._connection_widget._connect.clicked: GUIEvent.CONNECT,
            self._profile_widget._new.clicked: GUIEvent.NEW,
            self._profile_widget._remove.clicked: GUIEvent.REMOVE,
            self._profile_widget._rename.clicked: GUIEvent.RENAME,
            self._profile_widget._save.clicked: GUIEvent.SAVE,
            self._profile_widget._dropdown.activated: GUIEvent.SELECT
        }

        for signal, message in widget_event_map.items():
            signal.connect(
                lambda data=None, msg=message: self.send_event(msg, data)
            )

    def create_widget_update_hooks(self) -> None:
        event_handler_map = {
            self.INIT_DATA_RECEIVED: self._event_handler.initialise_widgets
        }

        for event, handler in event_handler_map.items():
            event.connect(handler)

    def request_init_data(self) -> None:
        self.send_event(GUIEvent.INIT, None)

    @property
    def rx_queue(self) -> multiprocessing.queues.Queue | None:
        return self._rx_queue

    @rx_queue.setter
    def rx_queue(self, queue: multiprocessing.queues.Queue) -> None:
        self._rx_queue = queue

    @property
    def tx_queue(self) -> multiprocessing.queues.Queue | None:
        return self._tx_queue

    @tx_queue.setter
    def tx_queue(self, queue: multiprocessing.queues.Queue) -> None:
        self._tx_queue = queue

    def send_event(self, message: str, data: ...) -> None:
        if self._tx_queue:
            self._tx_queue.put_nowait((message, data))

    def run(self):
        self.request_init_data()
        while True:
            if self._rx_queue and not self._rx_queue.empty():
                msg, data = self._rx_queue.get_nowait()
                if msg == IFEvent.INIT:
                    self.INIT_DATA_RECEIVED.emit(data)
