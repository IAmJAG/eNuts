# ==================================================================================
# src/fluxCore/types/interface/sockets/__frame.py
# ==================================================================================
from typing import Protocol, runtime_checkable


# ==================================================================================
@runtime_checkable
class iPacket(Protocol):
    def __init__(self, data: bytes): ...
    @property
    def createdAt(self) -> float: ...
    @property
    def payload(self) -> bytes: ...
