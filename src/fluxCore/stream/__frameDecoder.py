# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from av import VideoCodecContext


# ==================================================================================
class FrameDecoder:
    """Holds the active VideoCodecContext for ring publish. Decode is packet-side."""

    def __init__(self, codec: VideoCodecContext | None = None) -> None:
        self._codec: Optional[VideoCodecContext] = codec

    @classmethod
    def classname(cls) -> str:
        return cls.__name__

    @property
    def codec(self) -> Optional[VideoCodecContext]:
        return self._codec

    def setCodecContext(self, codec: VideoCodecContext | None) -> None:
        self._codec = codec


# ==================================================================================
__all__ = ["FrameDecoder"]
