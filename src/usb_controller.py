import multiprocessing

import libusb_package
import time
import usb.core
import usb.backend.libusb1

from usb_info import HIDInfo


class USBDeviceList:
    """Device list class for a given dance pad specification."""

    @staticmethod
    def connected_device_names(info: HIDInfo) -> list[str | None]:
        devs: list[usb.core.Device] = []
        for dev in libusb_package.find(
            find_all=True,  idVendor=info.VID, idProduct=info.PID
        ):
            devs.append(dev)
        return [dev.serial_number for dev in devs]

    @staticmethod
    def get_device_by_serial(
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


class HIDEndpointProcess(multiprocessing.Process):
    """Base class that manages a single HID endpoint in its own process."""

    def __init__(self, pad_info: HIDInfo, serial: str):
        super(HIDEndpointProcess, self).__init__()
        self._info = pad_info
        self._serial = serial
        self._queue = multiprocessing.Queue(maxsize=10)
        self._device = None
        self.start()

    def terminate(self) -> None:
        super().terminate()

    def run(self) -> None:
        self._device = USBDeviceList.get_device_by_serial(
            self._info.VID, self._info.PID, self._serial
        )
        if self._device is None:
            return
        while True:
            self._process()

    def _process(self) -> str | None:
        pass

    @property
    def queue(self) -> multiprocessing.Queue:
        return self._queue


class HIDReadProcess(HIDEndpointProcess):
    """Child class for reading data from an HID Endpoint."""

    TIMEOUT_MS = 1

    def _process(self) -> str | None:
        self._device: usb.core.Device
        sensor_data = self._device.read(
            self._info.READ_EP, self._info.BYTES, self.TIMEOUT_MS
        )
        if self._queue.full():
            self._queue.get_nowait()
        self._queue.put_nowait(sensor_data)


class HIDWriteProcess(HIDEndpointProcess):
    """Child class for writing data to an HID Endpoint."""

    TIMEOUT_SECS = 0.001

    def _process(self) -> str | None:
        self._device: usb.core.Device
        if not self._queue.empty():
            self._device.write(self._info.WRITE_EP, self._queue.get_nowait())
        else:
            time.sleep(self.TIMEOUT_SECS)
