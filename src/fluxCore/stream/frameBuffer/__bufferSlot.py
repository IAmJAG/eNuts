# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import CancelledError, Task
from asyncio import sleep as asyncSleep
from time import monotonic_ns
from typing import Dict, Optional, Tuple

# ==================================================================================
from ...types import DECODEFORMAT


# ==================================================================================
class BufferSlot:
    """
    Zero-copy decoded frame snapshot with multi-consumer lease and single timeout.
    """

    def __init__(
        self,  sequence: Optional[int] = None,  payload: Optional[DECODEFORMAT] = None, 
        pts: int = 0, width: int = 0, height: int = 0
    ) -> None:
        self._sequence: Optional[int] = monotonic_ns() if sequence is None else sequence
        self._pts: int = pts
        self._width: int = width
        self._height: int = height
        self._payload: Optional[DECODEFORMAT] = payload        
        self._consumers: Dict[int, Tuple[int, Task]] = dict[int, Tuple[int, Task]]()

    def acquire(self, consumerId: int, timeout: float) -> None:
        if self._payload is None:
            raise RuntimeError("cannot acquire empty slot")
        
        now: int = monotonic_ns()        
        newDeadline: int = 100 if timeout <= 0 else int(now + int(timeout * 1e-9))
                
        oldDeadline, task = self._consumers.get(consumerId, (0, None))        
        if task is not None and not task.done():
            if oldDeadline >= newDeadline: return
            newDeadline = oldDeadline

        self._cancelTimeout(consumerId)
        async def _watcher(deadline: int) -> None: 
            try:
                await asyncSleep(deadline)

            except CancelledError:
                pass

        task: Task = createTask(_watcher, newDeadline)
        task.add_done_callback(lambda: self.release(consumerId))
        self._consumers[consumerId] = (newDeadline, task)

    def release(self, consumerId: Optional[int] = None) -> None:
        if consumerId is None:
            for _, task in self._consumers.values():
                if not task.done(): task.cancel()

            self._consumers.clear()

        else:            
            self._cancelTimeout(consumerId)

    @property
    def isFree(self) -> bool:
        return len(self._consumers) == 0

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

    
    def _cancelTimeout(self, cId: int) -> None:
        _, task = self._consumers.pop(cId, (0, None))
        if not task.done(): task.cancel()

# ==================================================================================
__all__ = ["BufferSlot"]
# ==================================================================================
