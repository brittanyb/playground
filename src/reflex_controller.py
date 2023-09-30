from usb_controller import USBDeviceList, HIDReadProcess, HIDWriteProcess
from usb_info import ReflexV2Info


class ReflexPadInstance:
    """API to a connected RE:Flex v2 dance pad."""

    def __init__(self, info: ReflexV2Info, serial: str):
        self._serial = serial
        self._sensors_process = HIDReadProcess(info, serial)
        self._lights_process = HIDWriteProcess(info, serial)

    def disconnect(self) -> None:
        self._sensors_process.terminate()
        self._lights_process.terminate()

    @property
    def serial(self) -> str:
        return self._serial


class ReflexController:
    """USB controller for RE:Flex v2 dance pads."""

    def __init__(self):
        self._info = ReflexV2Info()
        self._instances = []
        self._serials = []
        self.enumerate_pads()

    def enumerate_pads(self) -> None:
        self._serials = USBDeviceList.connected_device_names(self._info)

    def connect_pad(self, serial: str) -> bool:
        pad = ReflexPadInstance(self._info, serial)
        if pad:
            self._instances.append(pad)
            self._serials.remove(serial)
            return True
        return False

    def disconnect_pad(self, serial: str) -> bool:
        for pad in self._instances:
            if isinstance(pad, ReflexPadInstance) and pad.serial == serial:
                pad.disconnect()
                self._instances.remove(pad)
                self._serials.append(serial)
                return True
        return False

    @property
    def available_pads(self) -> list[str | None]:
        return self._serials

    @property
    def connected_pads(self) -> list[ReflexPadInstance | None]:
        return self._instances

    @property
    def all_pads(self) -> list[str | None]:
        return [
            *self._serials,
            *[inst.serial for inst in self.connected_pads
              if isinstance(inst, ReflexPadInstance)]]
