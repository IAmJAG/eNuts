# ==================================================================================
from typing import Protocol, runtime_checkable

# ==================================================================================
from ..packets import iImagePacket
from .__socket import iSocket


# ==================================================================================
@runtime_checkable
class iVideoSocket(iSocket, Protocol):    
    async def asyncReceiveSingleFrame(self) -> iImagePacket: ...
    def receiveSingleFrame(self) -> iImagePacket: ...
    