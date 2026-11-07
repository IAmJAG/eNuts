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
    def __init__(
        self, payload: DECODEFORMAT = None, 
        sequence: Optional[float] = None,
        width: int = 0, height: int = 0, pts: int = 0
    ) -> None:
        self._sequence: float = sequence if sequence is not None else monotonic_ns()
        self._state: eSlotFlag = eSlotFlag.FREE
        self._width: int = width
        self._height: int = height
        self._pts: int = pts
        self._payload: DECODEFORMAT = payload

    def update(
        self, 
        payload: DECODEFORMAT, 
        sequence: Optional[float] = None, 
        width: int = 0, height: int = 0, pts: int = 0,
        state: eSlotFlag = eSlotFlag.WRITING
    ) -> None:
        self._state = state
        self._sequence = sequence if sequence is not None else monotonic_ns()
        self._width = width
        self._height = height
        self._pts = pts
        self._payload = payload

    @property
    def payload(self) -> DECODEFORMAT: 
        self._state = eSlotFlag.INUSE
        return self._payload

    @property
    def state(self) -> eSlotFlag: 
        return self._state

    @state.setter
    def state(self, value: eSlotFlag) -> None: 
        assert isinstance(value, eSlotFlag)
        self._state = value

    @property
    def sequence[T: eTimeDeltaFormat](self) -> float:
        return fromNanoSeconds(self._sequence, T)
    
    @property
    def pts(self) -> int: 
        return self._pts

    @property
    def width(self) -> int: 
        return self._width

    @property
    def height(self) -> int: 
        return self._height


# ==================================================================================
__all__ = ["RingSlot"]
# ==================================================================================