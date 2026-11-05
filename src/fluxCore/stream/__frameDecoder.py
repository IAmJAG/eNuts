# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Any, Callable, Optional, overload

# ==================================================================================
import numpy as np

# ==================================================================================
from av import VideoCodecContext

# ==================================================================================
from fluxCore.types.interface.packets import iFrame

# ==================================================================================
from .__eDecodeFormat import DECODEFORMAT, eDecodeFormat
from .__imageConverters import G_DECODE_FORMAT_MAP


# ==================================================================================
class FrameDecoder:    
    def __init__(self, codec: VideoCodecContext = None) -> None:
        self._codec: VideoCodecContext = codec

    @classmethod
    def classname(cls) -> str:
        return cls.__name__

    @property
    def codec(self) -> Optional[VideoCodecContext]:
        return self._codec

    def setCodecContext(self, codec: VideoCodecContext) -> None:
        self._codec = codec

    def decode(self, frame: iFrame, format: eDecodeFormat = eDecodeFormat.PIL) -> Optional[DECODEFORMAT]: 
        codec: VideoCodecContext = self._codec
        return G_DECODE_FORMAT_MAP[format](frame, codec)
    
