# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from ....types import DECODEFORMAT, eSlotFlag


# ==================================================================================
class RingSlot:
    """Reusable frame storage with explicit reader ownership."""

    def __init__(self) -> None:
        self._state: eSlotFlag = eSlotFlag.EMPTY
        self._sequence: int = 0
        self._pts: int = 0
        self._width: int = 0
        self._height: int = 0
        self._payload: Optional[DECODEFORMAT] = None
        self._readers: int = 0

    def beginWrite(self, sequence: int, pts: int, width: int = 0, height: int = 0) -> None:
        if self._readers:
            raise RuntimeError("RingSlot: cannot write while readers hold the slot")
        self._state = eSlotFlag.WRITING
        self._sequence = sequence
        self._pts = pts
        self._width = width
        self._height = height
        self._payload = None

    def completeWrite(
        self,
        payload: DECODEFORMAT,
        width: int,
        height: int,
        pts: Optional[int] = None,
    ) -> None:
        self._payload = payload
        self._width = width
        self._height = height
        if pts is not None:
            self._pts = pts
        self._state = eSlotFlag.FILLED

    def markFree(self) -> None:
        if self._readers:
            raise RuntimeError("RingSlot: cannot free while readers hold the slot")
        self._payload = None
        self._state = eSlotFlag.FREE

    def clear(self) -> None:
        if self._readers:
            raise RuntimeError("RingSlot: cannot clear while readers hold the slot")
        self._payload = None
        self._sequence = 0
        self._pts = 0
        self._width = 0
        self._height = 0
        self._state = eSlotFlag.EMPTY

    def acquire(self) -> None:
        if self._state is not eSlotFlag.FILLED or self._payload is None:
            raise RuntimeError("RingSlot: only filled slots can be acquired")
        self._readers += 1

    def release(self) -> None:
        if self._readers <= 0:
            raise RuntimeError("RingSlot: release without a matching acquire")
        self._readers -= 1

    @property
    def state(self) -> eSlotFlag:
        return self._state

    @property
    def sequence(self) -> int:
        return self._sequence

    @property
    def pts(self) -> int:
        return self._pts

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def payload(self) -> Optional[DECODEFORMAT]:
        return self._payload

    @property
    def readers(self) -> int:
        return self._readers

    @property
    def isWritable(self) -> bool:
        return self._readers == 0 and self._state in (eSlotFlag.EMPTY, eSlotFlag.FREE)


# ==================================================================================
__all__ = ["RingSlot"]
# ==================================================================================
