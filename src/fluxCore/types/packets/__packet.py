# ==================================================================================
# src/fluxCore/types/sockets/__packet.py
# ==================================================================================
from time import time

# ==================================================================================
from ..interface.packets import iPacket


# ==================================================================================
class Packet(iPacket):
    def __init__(self, data: bytes): 
        self._createdAt: float = time()
        self._payload: bytes = data
    
    @property
    def createdAt(self) -> float: 
        return self._createdAt
    
    @property
    def payload(self) -> bytes: 
        return self._payload
