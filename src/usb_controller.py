import multiprocessing

import libusb_package
import usb.core
import usb.backend.libusb1

from usb_info import HIDInfo


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


class HIDEndpointProcess(multiprocessing.Process):
    """Base class that manages a single HID endpoint in its own process."""

    def __init__(
            self, pad_info: HIDInfo, serial: str):
        super(HIDEndpointProcess, self).__init__()
        self._info = pad_info
        self._serial = serial
        self._queue = multiprocessing.Queue(maxsize=10)
        self._device = None
        self.start()

    def run(self) -> None:
        self._device = USBDeviceList.get_pad_by_serial(
            self._info.VID, self._info.PID, self._serial
        )
        while True:
            if not self._device:
                return
            try:
                self._process()
            except Exception as e:
                raise e

    def _process(self) -> str | None:
        pass

    @property
    def queue(self) -> multiprocessing.Queue:
        return self._queue


class HIDReadProcess(HIDEndpointProcess):
    """Child class for reading sensor data from an HID Endpoint."""

    def _process(self) -> str | None:
        self._device: usb.core.Device
        sensor_data = self._device.read(
            self._info.SENSORS_EP, self._info.BYTES
        )
        if self._queue.full():
            self._queue.get_nowait()
        self._queue.put_nowait(sensor_data)


class HIDWriteProcess(HIDEndpointProcess):
    """Child class for writing light data to an HID Endpoint."""

    def _process(self) -> str | None:
        self._device: usb.core.Device
        light_data = self._queue.get_nowait()
        self._device.write(self._info.LIGHTS_EP, light_data)
