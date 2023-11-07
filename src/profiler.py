import asyncio
import cProfile
import sys
import threading
import time


class Profiler:
    def __init__(self, timeout: int, fn: str):
        self._fn = fn
        self._timeout = timeout
        self.pr = cProfile.Profile()
        self.pr.enable()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.triggered = False

    def begin(self):
        self.triggered = True
        threading.Thread(target=self.run_asyncio_loop, daemon=True).start()

    def run_asyncio_loop(self):
        self.loop.run_until_complete(asyncio.sleep(self._timeout))
        self.end_profile()

    def end_profile(self):
        self.pr.disable()
        with open(self._fn, 'w') as f:
            stdout_val = sys.stdout
            sys.stdout = f
            self.pr.print_stats('cumulative')
            sys.stdout = stdout_val


class DeltaTimer:
    """Tracks time deviation from expectation over sample range."""

    def __init__(self, method: str, time_expected: float, num_samples: int):
        self._counter = 0
        self._samples = num_samples
        self._expected = time_expected
        self._last_time = time.time()
        self._delta = 0.0
        self._first_time = False
        self._method = method

    def count_samples(self) -> None:
        if self._first_time == False:
            print(f"{self._method}")
            self._last_time = time.time()
            self._first_time = True
            return None
        self._counter += 1
        if self._counter % self._samples == 0:
            current_time = time.time()
            self._delta += current_time - self._last_time - self._expected
            self._last_time = current_time
            print(f"{self._method}: {self._delta:8.5f} @ {self._samples}S")
