import multiprocessing

from led_data_handler import LEDDataHandler
from pad_model import PadModel
from reflex_controller import ReflexController
from sensor_data_handler import SensorDataHandler
from test_data_generator import TestPadWidget
from profile_controller import ProfileController


class InterfaceProcess(multiprocessing.Process):
    def __init__(
        self
    ):
        super(InterfaceProcess, self).__init__()
        self._rx_queue = multiprocessing.Queue()
        self._tx_queue = multiprocessing.Queue()
        self.daemon = True

    def run(self) -> None:
        self.led_handler = LEDDataHandler()
        self.sensor_handler = SensorDataHandler()
        self.pad_model = PadModel()
        self.pad_controller = ReflexController()
        self.profile_controller = ProfileController(self.pad_model)
        self.tester = TestPadWidget(self.pad_model)
        while True:
            if self._rx_queue and not self._rx_queue.empty():
                msg = self._rx_queue.get_nowait()
                print(msg)
                self._tx_queue.put_nowait(f"{msg}ed")

    @property
    def rx_queue(self) -> multiprocessing.Queue:
        return self._rx_queue

    @property
    def tx_queue(self) -> multiprocessing.Queue:
        return self._tx_queue
