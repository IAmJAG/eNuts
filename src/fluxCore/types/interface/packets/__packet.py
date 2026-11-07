# ==================================================================================
from typing import Protocol, runtime_checkable

# ==================================================================================
from ...__eTimeDeltaFormat import eTimeDeltaFormat


# ==================================================================================
@runtime_checkable
class iPacket(Protocol):
    def __init__(self, data: bytes, width: int = 0, height: int = 0): ...
    @property
    def createdAt(self) -> float: ...
    @property
    def payload(self) -> bytes: ...
    @property
    def width(self) -> int: ...
    @property
    def height(self) -> int: ...
