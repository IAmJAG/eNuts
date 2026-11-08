# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional, Union

# ==================================================================================
from ....types import DECODEFORMAT
from .__slotFlag import eSlotFlag


# ==================================================================================
class RingSlot:
    """Single ring cell. State only changes via beginWrite/completeWrite/markFree/clear."""

    def __init__(self) -> None:
        self._state: eSlotFlag = eSlotFlag.EMPTY
        # packet.createdAt (iPacket); comparable for latest()
        self._sequence: float = 0.0
        self._pts: int = 0
        self._width: int = 0
        self._height: int = 0
        self._payload: Optional[DECODEFORMAT] = None

    def beginWrite(
        self,
        sequence: Union[int, float],
        pts: int,
        width: int = 0,
        height: int = 0,
    ) -> None:
        self._state = eSlotFlag.WRITING
        self._sequence = float(sequence)
        self._pts = int(pts)
        self._width = int(width)
        self._height = int(height)
        self._payload = None

    def completeWrite(
        self,
        payload: DECODEFORMAT,
        width: int,
        height: int,
        pts: Optional[int] = None,
    ) -> None:
        self._payload = payload
        self._width = int(width)
        self._height = int(height)
        if pts is not None:
            self._pts = int(pts)
        self._state = eSlotFlag.FILLED

    def markFree(self) -> None:
        self._payload = None
        self._state = eSlotFlag.FREE

    def clear(self) -> None:
        self._payload = None
        self._sequence = 0.0
        self._pts = 0
        self._width = 0
        self._height = 0
        self._state = eSlotFlag.EMPTY

    @property
    def state(self) -> eSlotFlag:
        return self._state

    @property
    def sequence(self) -> float:
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
        """Read-only. Does not change state."""
        return self._payload

    @property
    def isWritable(self) -> bool:
        return self._state in (eSlotFlag.EMPTY, eSlotFlag.FREE)


# ==================================================================================
__all__ = ["RingSlot"]
# ==================================================================================
