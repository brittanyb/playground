from multiprocessing.sharedctypes import SynchronizedArray
from multiprocessing.synchronize import Event


class LEDDataHandler:
    """Converts lights data from PadModel to RE:Flex Dance format."""

    def __init__(self, data: SynchronizedArray, event: Event):
        self._data = data
        self._event = event

    def give_sample(self) -> None:
        if not self._event.is_set():
            return
        with self._data.get_lock():
            for i in range(64):
                self._data[i] = 0
        self._event.clear()
