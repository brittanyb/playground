import multiprocessing.queues
import time

import PySide6.QtCore as QtCore

from event_info import WidgetMessage
from gui_widgets import Widgets


class GUIThread(QtCore.QThread):
    """Thread for GUI that handles event data TX/RX to data process."""

    TIMEOUT_SECS = 0.005

    def __init__(self, widgets: Widgets):
        super(GUIThread, self).__init__()
        self._rx_queue = None
        self._tx_queue = None
        self._widgets = widgets
        for signal, message in self._widgets.hooks.items():
            signal.connect(lambda *, message=message: self.send_event(message))
        for signal, handler in self._widgets.signal_handlers.items():
            signal.connect(handler)

    def send_event(self, message: str) -> None:
        data = []
        for request in self._widgets.data_requests[message]:
            data.append(request())
        if self._tx_queue:
            self._tx_queue.put_nowait((message, data))

    def run(self):
        self.send_event(WidgetMessage.INIT)
        while True:
            if self._rx_queue and not self._rx_queue.empty():
                message, data = self._rx_queue.get_nowait()
                self._widgets.process_requests[message].emit(data)
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
