# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional, Protocol, runtime_checkable

# ==================================================================================
from .....types import DECODEFORMAT

# ==================================================================================
@runtime_checkable
class iBufferSlot(Protocol):
    def release(self, consumerId: Optional[int] = None) -> None: ...
    @property
    def sequence(self) -> int: ...
    @property
    def payload(self) -> Optional[DECODEFORMAT]: ...
    @property
    def isLocked(self) -> bool: ...
    @property
    def isFree(self) -> bool: ...

# ==================================================================================
__all__ = ["iBufferSlot"]
# ==================================================================================
