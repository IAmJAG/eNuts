# ==================================================================================
# src/fluxCore/types/interface/sockets/__videoSocket.py
# ==================================================================================
from typing import Protocol, runtime_checkable

# ==================================================================================
from ..sockets import iFrame
from .__socket import iSocket


# ==================================================================================
@runtime_checkable
class iVideoSocket(iSocket, Protocol):    
    async def receiveSingleFrame(self) -> iFrame: ...
    