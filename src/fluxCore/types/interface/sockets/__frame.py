# ==================================================================================
# src/fluxCore/types/interface/sockets/__frame.py
# ==================================================================================
from typing import TYPE_CHECKING, Protocol, runtime_checkable

# ==================================================================================
from av import VideoFrame
from torch import Tensor

# ==================================================================================
from .__packet import iPacket


# ==================================================================================
@runtime_checkable
class iFrame(iPacket, Protocol):
    def __init__(self, data: bytes, pts: int, isConfig: bool,isKeyFrame: bool, device: str = "GPU"): ...
    @property
    def isKeyFrame(self) -> bool: ...
    @property
    def isConfig(self) -> bool: ...
    @property
    def pts(self) -> int: ...
    def decode(self, ) -> VideoFrame | Tensor: ...
    