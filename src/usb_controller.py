import multiprocessing
import time

import libusb_package
import usb.core
import usb.backend.libusb1

from usb_info import HIDInfo, ReflexV2Info


class USBDeviceList:
    """Device list class for a given dance pad specification."""

    @staticmethod
    def connected_pad_names(pad_info: HIDInfo) -> list[str | None]:
        pads: list[usb.core.Device] = []
        for dev in libusb_package.find(
            find_all=True,  idVendor=pad_info.VID, idProduct=pad_info.PID
        ):
            pads.append(dev)
        return [pad.serial_number for pad in pads]

    @staticmethod
    def get_pad_by_serial(
        vid: int, pid: int, serial: str
    ) -> usb.core.Device | None:
        devices: list[usb.core.Device] | None = libusb_package.find(
            find_all=True, idVendor=vid, idProduct=pid
        )
        if devices is None:
            return
        for device in devices:
            if device.serial_number == serial:
                return device


class DancePadProcess(multiprocessing.Process):
    """Separate process runner for a dance pad with custom I/O IPC."""

    def __init__(
            self, pad_info: HIDInfo, serial: str,
    ):
        super(DancePadProcess, self).__init__()
        self._info = pad_info
        self._serial = serial

    def run(self) -> None:
        index = 0
        self._device = USBDeviceList.get_pad_by_serial(
            self._info.VID, self._info.PID, self._serial
        )
        while (True):
            if not self._device:
                break
            sensor_data = self._device.read(
                self._info.SENSORS_EP, self._info.BYTES
            )
            index += 1
            if (index % 500 == 0):
                print(sensor_data)


if __name__ == "__main__":
    pad_info = ReflexV2Info()
    serials = USBDeviceList.connected_pad_names(pad_info)
    if isinstance(serials[0], str):
        process = DancePadProcess(pad_info, serials[0])
        process.start()
        time.sleep(5)
        process.terminate()
