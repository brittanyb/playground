import asyncio
import cProfile
import sys
import threading


class Profiler:
    def __init__(self, timeout: int, fn: str):
        self._fn = fn
        self._timeout = timeout
        self.pr = cProfile.Profile()
        self.pr.enable()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
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
