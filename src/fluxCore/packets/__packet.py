# ==================================================================================
from __future__ import annotations

# ==================================================================================
from time import monotonic_ns

# ==================================================================================
from ..types import eTimeDeltaFormat


# ==================================================================================
class Packet:
    def __init__(self, data: bytes): 
        self._createdAt: float = monotonic_ns()
        self._payload: bytes = data
    
    @property
    def createdAt(self) -> float:
        return self._createdAt
    
    @property
    def payload(self) -> bytes: 
        return self._payload

    @property
    def format(self, format: eTimeDeltaFormat) -> float:
        if format == eTimeDeltaFormat.SECONDS: 
            return self._createdAt / 1_000_000_000
        
        elif format == eTimeDeltaFormat.MILLISECONDS:
            return self._createdAt / 1_000_000
        
        elif format == eTimeDeltaFormat.MICROSECONDS:
            return self._createdAt / 1_000

        return self._createdAt
