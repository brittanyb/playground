import multiprocessing

from data_sequences import Sequences


class DataProcess(multiprocessing.Process):
    """Main process for data handling."""

    def __init__(self):
        super(DataProcess, self).__init__()
        self._rx_queue = multiprocessing.Queue()
        self._tx_queue = multiprocessing.Queue()

    def send_event(self, message: str, data: ... = None):
        self._tx_queue.put_nowait((message, data))

    def run(self) -> None:
        self._sequences = Sequences()
        while True:
            self._sequences.handle_pad_data()
            if not self._rx_queue.empty():
                self.handle_events()

    def handle_events(self):
        rx_mes, rx_data = self._rx_queue.get_nowait()
        requested_methods = self._sequences.receive.get(rx_mes, [])
        for request in requested_methods:
            tx_data = request(*rx_data)
            if tx_data is None:
                continue
            tx_mes = self._sequences.transmit.get(request, None)
            if tx_mes is None:
                continue
            self.send_event(tx_mes, tx_data)

    @property
    def rx_queue(self) -> multiprocessing.Queue:
        return self._rx_queue

    @property
    def tx_queue(self) -> multiprocessing.Queue:
        return self._tx_queue
