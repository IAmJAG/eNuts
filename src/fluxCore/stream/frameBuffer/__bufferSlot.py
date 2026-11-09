# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import CancelledError, Task, create_task, get_running_loop, sleep
from threading import Lock
from typing import Optional, Set

# ==================================================================================
from ...types import DECODEFORMAT


# ==================================================================================
class BufferSlot:
    """Zero-copy decoded frame snapshot with multi-consumer lease and single timeout."""

    def __init__(self) -> None:
        self._sequence: int = 0
        self._pts: int = 0
        self._width: int = 0
        self._height: int = 0
        self._payload: Optional[DECODEFORMAT] = None
        self._consumers: Set[int] = set()
        self._lock: Lock = Lock()
        self._timeoutTask: Optional[Task] = None
        self._timeout: float = 0.0

    def write(self, sequence: int, payload: DECODEFORMAT, pts: int, width: int, height: int) -> None:
        with self._lock:
            self._sequence = sequence
            self._payload = payload
            self._pts = pts
            self._width = width
            self._height = height
            self._consumers.clear()
            self._cancelTimeout()

    def acquire(self, consumerId: int, timeout: float) -> None:
        with self._lock:
            if self._payload is None:
                raise RuntimeError("BufferSlot: cannot acquire empty slot")
            self._consumers.add(consumerId)
            self._timeout = timeout
            self._armTimeout(timeout)

    def release(self, consumerId: Optional[int] = None) -> None:
        with self._lock:
            if consumerId is None:
                self._consumers.clear()
            else:
                self._consumers.discard(consumerId)
            if not self._consumers:
                self._cancelTimeout()
                self._payload = None

    @property
    def isLocked(self) -> bool:
        with self._lock:
            return len(self._consumers) > 0

    @property
    def isFree(self) -> bool:
        return not self.isLocked

    @property
    def sequence(self) -> int:
        return self._sequence

    @property
    def payload(self) -> Optional[DECODEFORMAT]:
        return self._payload

    @property
    def pts(self) -> int:
        return self._pts

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    def _armTimeout(self, timeout: float) -> None:
        self._cancelTimeout()
        if timeout <= 0:
            return
        try:
            loop = get_running_loop()
        except RuntimeError:
            return
        self._timeoutTask = loop.create_task(self._timeoutWatcher(timeout))

    def _cancelTimeout(self) -> None:
        task = self._timeoutTask
        if task is not None and not task.done():
            task.cancel()
        self._timeoutTask = None

    async def _timeoutWatcher(self, timeout: float) -> None:
        try:
            await sleep(timeout)
            self.release()
        except CancelledError:
            pass

# ==================================================================================
__all__ = ["BufferSlot"]
# ==================================================================================
