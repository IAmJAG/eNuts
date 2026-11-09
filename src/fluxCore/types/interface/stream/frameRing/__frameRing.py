# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional, Protocol, runtime_checkable

# ==================================================================================
from av import VideoCodecContext

# ==================================================================================
from ...packets import iImagePacket
from .slot import iRingSlot


# ==================================================================================
@runtime_checkable
class iFrameRing(Protocol):
    async def publish(self, packet: iImagePacket, decoder: Optional[VideoCodecContext] = None) -> None: ...
    def start(self) -> None: ...
    async def stop(self) -> None: ...
    def latest(self) -> Optional[iRingSlot]: ...
    async def next(self, currentSequence: Optional[int] = None) -> Optional[iRingSlot]: ...
    def release(self, slot: iRingSlot) -> None: ...
    @property
    def size(self) -> int: ...
    @property
    def pending(self) -> int: ...


# ==================================================================================
__all__ = ["iFrameRing"]
# ==================================================================================
