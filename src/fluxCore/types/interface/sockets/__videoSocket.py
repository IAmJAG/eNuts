# ==================================================================================
# src/fluxCore/types/interface/sockets/__videoSocket.py
# ==================================================================================
from typing import Protocol, runtime_checkable

# ==================================================================================
from ..packets import iFrame
from .__socket import iSocket


# ==================================================================================
@runtime_checkable
class iVideoSocket(iSocket, Protocol):    
    async def asyncReceiveSingleFrame(self) -> iFrame: ...
    def receiveSingleFrame(self) -> iFrame: ...
    