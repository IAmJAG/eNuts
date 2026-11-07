# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Protocol, runtime_checkable

# ==================================================================================
from av import CodecContext

# ==================================================================================
from ...__eDecodeFormat import DECODEFORMAT
from .__packet import iPacket


# ==================================================================================
@runtime_checkable
class iImagePacket[T: DECODEFORMAT](iPacket, Protocol):
    @property
    def isKeyFrame(self) -> bool: ...
    @property
    def isConfig(self) -> bool: ...
    @property
    def pts(self) -> int: ...
    def decode(self, decoder: CodecContext) -> T: ...
    