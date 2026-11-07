# ==================================================================================
from typing import Protocol, runtime_checkable

# ==================================================================================
from ...__eTimeDeltaFormat import eTimeDeltaFormat


# ==================================================================================
@runtime_checkable
class iPacket(Protocol):
    @property
    def createdAt(self) -> float: ...
    @property
    def payload(self) -> bytes: ...
    @property
    def format(self, format: eTimeDeltaFormat) -> float: ...
