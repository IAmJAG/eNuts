# ==================================================================================
from __future__ import annotations

# ==================================================================================
from jAGFx.configuration import Configuration
from jAGFx.types.interface.configuration import iConfiguration

# ==================================================================================
class RingSlotConfiguration(Configuration, iConfiguration):
    """Configuration section for FrameBuffer / BufferSlot limits and timeout."""

    def __init__(self) -> None:
        super().__init__()
        self._bufferSizeMin: int = 4
        self._bufferSizeMax: int = 256
        self._vramCap: float = 0.85
        self._defaultReleaseTimeout: float = 5.0
        self.Properties.extend([
            "bufferSizeMin",
            "bufferSizeMax",
            "vramCap",
            "defaultReleaseTimeout",
        ])

    @property
    def bufferSizeMin(self) -> int:
        return self._bufferSizeMin

    @property
    def bufferSizeMax(self) -> int:
        return self._bufferSizeMax

    @property
    def vramCap(self) -> float:
        return self._vramCap

    @property
    def defaultReleaseTimeout(self) -> float:
        return self._defaultReleaseTimeout

# ==================================================================================
__all__ = ["RingSlotConfiguration"]
# ==================================================================================
