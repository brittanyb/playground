import multiprocessing
import time

from event_info import DataProcessMessage, WidgetMessage
from led_data_handler import LEDDataHandler
from pad_model import PadModel
from profile_controller import ProfileController
from reflex_controller import ReflexController
from sensor_data_handler import SensorDataHandler


class DataProcess(multiprocessing.Process):
    """Main process for data handling."""

    TIMEOUT_SECS = 0.0002

    def __init__(self):
        super(DataProcess, self).__init__()
        self._rx_queue = multiprocessing.Queue()
        self._tx_queue = multiprocessing.Queue()

    def create_receive_sequences(self) -> None:
        self._receive_sequences = {
            WidgetMessage.INIT: [
                self._pad_controller.get_all_pads,
                self._profile_controller.get_profile_names
            ],
            WidgetMessage.CONNECT: [
                self._pad_controller.toggle_pad_connection
            ],
            WidgetMessage.REFRESH: [
                self._pad_controller.enumerate_pads,
                self._pad_controller.get_all_pads
            ],
            WidgetMessage.QUIT: [
                self._pad_controller.disconnect_pad
            ]
        }

    def create_transmit_sequences(self) -> None:
        self._transmit_sequences = {
            self._pad_controller.get_all_pads:
                DataProcessMessage.ALL_PADS,
            self._profile_controller.get_profile_names:
                DataProcessMessage.PROFILE_NAMES,
            self._pad_controller.toggle_pad_connection:
                DataProcessMessage.PAD_CONNECTED
        }

    def create_data_managers(self):
        self._led_handler = LEDDataHandler()
        self._sensor_handler = SensorDataHandler()
        self._pad_model = PadModel()
        self._pad_controller = ReflexController()
        self._profile_controller = ProfileController(self._pad_model)

    def send_event(self, message: str, data: ... = None):
        print(f"DP sends: {message}: {data}")
        self._tx_queue.put_nowait((message, data))

    def run(self) -> None:
        self.create_data_managers()
        self.create_receive_sequences()
        self.create_transmit_sequences()
        while True:
            if not self._rx_queue.empty():
                message, data = self._rx_queue.get_nowait()
                requests = self._receive_sequences.get(message, [])
                print(f"DP triggers: {[r.__name__ for r in requests]}")
                for request in requests:
                    if (res := request(*data)) is not None:
                        if msg := self._transmit_sequences.get(request, None):
                            self.send_event(msg, res)
            else:
                time.sleep(self.TIMEOUT_SECS)

    @property
    def rx_queue(self) -> multiprocessing.Queue:
        return self._rx_queue

    @property
    def tx_queue(self) -> multiprocessing.Queue:
        return self._tx_queue
