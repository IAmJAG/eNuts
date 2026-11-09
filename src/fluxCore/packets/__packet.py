# ==================================================================================
from __future__ import annotations

# ==================================================================================
from time import monotonic_ns

# ==================================================================================
from utilities import fromNanoSeconds

# ==================================================================================
from ..types import eTimeDeltaFormat
from ..types.interface.packets import iPacket


# ==================================================================================
class Packet(iPacket):
    def __init__(self, data: bytes, width: int = 0, height: int = 0):
        self._createdAt: int = monotonic_ns()
        self._payload: bytes = data
        self._width: int = width
        self._height: int = height

    def getCreatedAt(self, format: eTimeDeltaFormat = eTimeDeltaFormat.NANOSECONDS) -> float:
        return fromNanoSeconds(self._createdAt, format)

    @property
    def createdAt(self) -> int:
        return self._createdAt

    @property
    def payload(self) -> bytes:
        return self._payload

    @property
    def width(self) -> int:
        return self._width

    @width.setter
    def width(self, value: int) -> None:
        self._width = value

    @property
    def height(self) -> int:
        return self._height

    @height.setter
    def height(self, value: int) -> None:
        self._height = value
