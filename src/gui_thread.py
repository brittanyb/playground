import multiprocessing.queues
import time

import PySide6.QtCore as QtCore

from connection_widget import ConnectionWidget
from gui_handlers import GUIHandlers
from event_info import WidgetMessage, DataProcessMessage, DataReceiveSignaller
from pad_widget import PadWidget
from profile_widget import ProfileWidget


class GUIThread(QtCore.QThread):
    """Thread for GUI that handles event data TX/RX to data process."""

    TIMEOUT_SECS = 0.001

    def __init__(
        self, connection_widget: ConnectionWidget, pad_widget: PadWidget,
        profile_widget: ProfileWidget
    ):
        super(GUIThread, self).__init__()
        self._connection_widget = connection_widget
        self._pad_widget = pad_widget
        self._profile_widget = profile_widget
        self._signals = DataReceiveSignaller()
        self._handlers = GUIHandlers(
            self._connection_widget, self._pad_widget, self._profile_widget
        )
        self._rx_queue = None
        self._tx_queue = None
        self.create_widget_event_message_hooks()
        self.create_widget_data_hooks()
        self.create_widget_update_hooks()
        self.create_widget_handler_hooks()

    def create_widget_event_message_hooks(self) -> None:
        hooks = {
            self._connection_widget.CONNECT_CLICKED: WidgetMessage.CONNECT,
            self._connection_widget.REFRESH_CLICKED: WidgetMessage.REFRESH,
            self._pad_widget.FRAME_READY: WidgetMessage.FRAME_READY
        }
        for signal, message in hooks.items():
            signal.connect(lambda message=message: self.send_event(message))

    def create_widget_data_hooks(self) -> None:
        self._data_requests = {
            WidgetMessage.INIT: [],
            WidgetMessage.CONNECT: [self._connection_widget.get_pad_serial],
            WidgetMessage.REFRESH: [],
            WidgetMessage.QUIT: [],
            WidgetMessage.FRAME_READY: [],
        }

    def create_widget_update_hooks(self) -> None:
        self._process_requests = {
            DataProcessMessage.ALL_PADS: self._signals.ALL_PADS,
            DataProcessMessage.PROFILE_NAMES: self._signals.PROFILE_NAMES,
            DataProcessMessage.PAD_CONNECTED: self._signals.PAD_CONNECTED,
            DataProcessMessage.FRAME_DATA: self._signals.FRAME_DATA
        }

    def create_widget_handler_hooks(self) -> None:
        self._signal_handlers = {
            self._signals.ALL_PADS: self._handlers.all_pads_received,
            self._signals.PROFILE_NAMES: self._handlers.profile_names_received,
            self._signals.PAD_CONNECTED: self._handlers.pad_connected,
            self._signals.FRAME_DATA: self._handlers.frame_data_received
        }
        for signal, handler in self._signal_handlers.items():
            signal.connect(handler)

    def send_event(self, message: str) -> None:
        data = []
        for request in self._data_requests[message]:
            data.append(request())
        if self._tx_queue:
            self._tx_queue.put_nowait((message, data))

    def run(self):
        self.send_event(WidgetMessage.INIT)
        while True:
            if self._rx_queue and not self._rx_queue.empty():
                message, data = self._rx_queue.get_nowait()
                self._process_requests[message].emit(data)
            else:
                time.sleep(self.TIMEOUT_SECS)

    def terminate(self) -> None:
        self.send_event(WidgetMessage.QUIT)
        super().terminate()

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
