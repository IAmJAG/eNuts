# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional, Protocol, runtime_checkable

# ==================================================================================
from .....types import DECODEFORMAT
from .__bufferSlot import iBufferSlot

# ==================================================================================
@runtime_checkable
class iFrameBuffer(Protocol):
    def publish(self, sequence: int, payload: DECODEFORMAT, pts: int, width: int, height: int) -> None: ...
    def next(self, consumerId: int, sequence: Optional[int] = None, timeout: Optional[float] = None) -> Optional[iBufferSlot]: ...
    @property
    def size(self) -> int: ...

# ==================================================================================
__all__ = ["iFrameBuffer"]
# ==================================================================================
