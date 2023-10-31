import multiprocessing
import time

from data_sequences import Sequences


class DataProcess(multiprocessing.Process):
    """Main process for data handling."""

    TIMEOUT_SECS = 0.0002

    def __init__(self):
        super(DataProcess, self).__init__()
        self._rx_queue = multiprocessing.Queue()
        self._tx_queue = multiprocessing.Queue()

    def send_event(self, message: str, data: ... = None):
        self._tx_queue.put_nowait((message, data))

    def run(self) -> None:
        sequences = Sequences()
        while True:
            if not self._rx_queue.empty():
                message, data = self._rx_queue.get_nowait()
                requests = sequences.receive.get(message, [])
                for request in requests:
                    if (res := request(*data)) is not None:
                        if msg := sequences.transmit.get(request, None):
                            self.send_event(msg, res)
            else:
                time.sleep(self.TIMEOUT_SECS)

    @property
    def rx_queue(self) -> multiprocessing.Queue:
        return self._rx_queue

    @property
    def tx_queue(self) -> multiprocessing.Queue:
        return self._tx_queue
