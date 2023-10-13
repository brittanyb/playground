import multiprocessing.queues
import threading

from connection_widget import ConnectionWidget
from pad_widget import PadWidget
from profile_widget import ProfileWidget


class GUIEventManager(threading.Thread):

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

        self.create_widget_hooks()

    def create_widget_hooks(self) -> None:
        widget_event_map = {
            self._connection_widget._refresh.clicked: "refresh",
            self._connection_widget._connect.clicked: "connect",
            self._profile_widget._new.clicked: "new",
            self._profile_widget._remove.clicked: "remove",
            self._profile_widget._rename.clicked: "rename",
            self._profile_widget._save.clicked: "save",
            self._profile_widget._dropdown.activated: "select"
        }

        for signal, message in widget_event_map.items():
            signal.connect(lambda _=False, msg=message: self.send_event(msg))

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

    def send_event(self, message: str) -> None:
        if self._tx_queue:
            self._tx_queue.put_nowait(message)

    def run(self):
        while True:
            if self._rx_queue and not self._rx_queue.empty():
                msg = self._rx_queue.get()
                print(msg)
