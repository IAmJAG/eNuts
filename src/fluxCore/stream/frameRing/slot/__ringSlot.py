# ==================================================================================
from __future__ import annotations

# ==================================================================================
from time import monotonic_ns
from typing import Optional

# ==================================================================================
from utilities import fromNanoSeconds

from ....packets import TensorPacket

# ==================================================================================
from ....types import DECODEFORMAT, eTimeDeltaFormat
from ...__frameFlags import FrameFlags
from .__slotFlag import eSlotFlag


# ==================================================================================
class RingSlot:
    def __init__(self) -> None:
        self._state: eSlotFlag = eSlotFlag.EMPTY
        self._sequence: int = 0  # monotonic_ns at accept
        self._pts: int = 0
        self._width: int = 0
        self._height: int = 0
        self._payload: Optional[DECODEFORMAT] = None

    def beginWrite( self, sequence: int, pts: int, width: int = 0, height: int = 0) -> None:
        self._state = eSlotFlag.WRITING
        self._sequence = sequence
        self._pts = pts
        self._width = width
        self._height = height
        self._payload = None

    def completeWrite(
        self, payload: DECODEFORMAT,
        width: int, height: int, pts: Optional[int] = None,
    ) -> None:
        self._payload = payload
        self._width = width
        self._height = height
        if pts is not None: self._pts = pts
        self._state = eSlotFlag.FILLED

    def markFree(self) -> None:
        self._payload = None
        self._state = eSlotFlag.FREE

    def clear(self) -> None:
        self._payload = None
        self._sequence = 0
        self._pts = 0
        self._width = 0
        self._height = 0
        self._state = eSlotFlag.EMPTY

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
    def isWritable(self) -> bool:
        return self._state in (eSlotFlag.EMPTY, eSlotFlag.FREE)


# ==================================================================================
__all__ = ["RingSlot"]
# ==================================================================================
