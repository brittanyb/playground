from led_data_handler import LEDDataHandler
from pad_model import Coord
from sensor_data_handler import SensorDataHandler
from usb_controller import USBDeviceList, HIDReadProcess, HIDWriteProcess
from usb_info import ReflexV2Info


class ReflexPadInstance:
    """API to a connected RE:Flex v2 dance pad."""

    def __init__(self, info: ReflexV2Info, serial: str):
        self._serial = serial
        self._read = HIDReadProcess(info, serial)
        self._write = HIDWriteProcess(info, serial)
        self._sensors = SensorDataHandler(self._read.data, self._read.event)
        self._lights = LEDDataHandler(self._write.data, self._write.event)

    def disconnect(self) -> None:
        self._read.terminate()
        self._write.terminate()

    def handle_sensor_data(self) -> None:
        self._sensors.take_sample()

    def handle_light_data(self) -> None:
        self._lights.give_sample()

    @property
    def pad_data(self) -> dict[tuple[Coord, Coord], int]:
        return self._sensors.pad_data

    @property
    def serial(self) -> str:
        return self._serial


class ReflexController:
    """USB controller for RE:Flex v2 dance pads."""

    CONNECTED = True
    DISCONNECTED = False

    def __init__(self):
        self._info = ReflexV2Info()
        self._instance = None
        self._serials = []
        self.enumerate_pads()

    def enumerate_pads(self) -> None:
        self._serials = USBDeviceList.connected_device_names(self._info)

    def toggle_pad_connection(self, serial: str) -> bool:
        if self._instance:
            return self.disconnect_pad()
        else:
            return self.connect_pad(serial)

    def connect_pad(self, serial: str) -> bool:
        if pad := ReflexPadInstance(self._info, serial):
            if self._instance is None and serial in self._serials:
                self._instance = pad
                return self.CONNECTED
        return self.DISCONNECTED

    def disconnect_pad(self) -> bool:
        if self._instance is None:
            return self.DISCONNECTED
        self._instance.disconnect()
        self._instance = None
        return self.DISCONNECTED

    def get_all_pads(self) -> list[str | None]:
        return self._serials

    @property
    def pad(self) -> ReflexPadInstance | None:
        if self._instance:
            return self._instance
        return None
