# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional, Protocol, runtime_checkable

# ==================================================================================
from av import VideoCodecContext

# ==================================================================================
from ....__eDecodeFormat import DECODEFORMAT
from ...packets import iImagePacket
from .slot import iRingSlot


# ==================================================================================
@runtime_checkable
class iFrameRing(Protocol):
    def publish(self, packet: iImagePacket, decoder: VideoCodecContext) -> None: ...
    def latest(self) -> Optional[DECODEFORMAT]: ...
    def next(self) -> Optional[DECODEFORMAT]: ...
    def release(self, slot: iRingSlot) -> None: ...
    @property
    def size(self) -> int: ...

# ==================================================================================
__all__ = ["iFrameRing"]
# ==================================================================================
