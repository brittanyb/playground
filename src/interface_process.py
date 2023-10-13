import multiprocessing

from gui_event import GUIEvent
from interface_event import IFEvent
from led_data_handler import LEDDataHandler
from pad_model import PadModel
from profile_controller import ProfileController
from reflex_controller import ReflexController
from sensor_data_handler import SensorDataHandler
from test_data_generator import TestPadWidget


class InterfaceProcess(multiprocessing.Process):
    """Main process for data handling."""

    def __init__(self):
        super(InterfaceProcess, self).__init__()
        self._rx_queue = multiprocessing.Queue()
        self._tx_queue = multiprocessing.Queue()
        self.daemon = True

    def send_event(self, message: str, data: ... = None):
        self._tx_queue.put_nowait((message, data))

    def run(self) -> None:
        self._led_handler = LEDDataHandler()
        self._sensor_handler = SensorDataHandler()
        self._pad_model = PadModel()
        self._pad_controller = ReflexController()
        self._profile_controller = ProfileController(self._pad_model)
        self._tester = TestPadWidget(self._pad_model)
        while True:
            if self._rx_queue and not self._rx_queue.empty():
                msg, data = self._rx_queue.get_nowait()
                if msg == GUIEvent.INIT:
                    pad_list = self._pad_controller.all_pads
                    profile_list = self._profile_controller.profile_names
                    self.send_event(IFEvent.INIT, [pad_list, profile_list])
                if msg == GUIEvent.CONNECT:
                    self._tx_queue.put_nowait(self._pad_controller.all_pads)

    @property
    def rx_queue(self) -> multiprocessing.Queue:
        return self._rx_queue

    @property
    def tx_queue(self) -> multiprocessing.Queue:
        return self._tx_queue
