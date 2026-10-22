# Game time in milliseconds: the wall clock, or a virtual one that only moves
# when the engine says so (1 ms per frame, plus every sleep), which makes a
# run repeatable.
from __future__ import annotations

import time


class Clock:
    # virtual: bool
    # t: int
    # start: float
    # While paused, game time stands still: the wall clock time it stopped
    # at, or a negative value when running.
    # paused_at: float

    def __init__(self, virtual: bool) -> None:
        self.virtual = virtual
        self.t = 0
        self.start = time.monotonic()
        self.paused_at = -1.0

    def now(self) -> int:
        if self.virtual:
            return self.t
        wall = self.paused_at if self.paused_at >= 0.0 else time.monotonic()
        return int((wall - self.start) * 1000.0)

    def pause(self) -> None:
        if self.paused_at < 0.0:
            self.paused_at = time.monotonic()

    def resume(self) -> None:
        """Game time goes on from where it stopped: the pause takes no time."""
        if self.paused_at >= 0.0:
            self.start += time.monotonic() - self.paused_at
            self.paused_at = -1.0

    def tick(self) -> None:
        if self.virtual:
            self.t += 1

    def sleep(self, ms: int) -> None:
        if self.virtual:
            self.t += ms
        else:
            time.sleep(ms / 1000)
