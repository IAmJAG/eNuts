# ==================================================================================
# src/fluxCore/types/interface/emitters/__SCRCPYEmitter.py
# ==================================================================================
from typing import Protocol, runtime_checkable

# ==================================================================================
from av import VideoCodecContext

# ==================================================================================
from jAGFx.types.interface.services import iService, iSubscription

# ==================================================================================
from ..devices import iSCRCPY
from ..sockets import iControlSocket


# ==================================================================================
@runtime_checkable
class iSCRCPYEmitter(iSCRCPY, iService, iSubscription, Protocol):
    async def initialize(self) -> None: ...

    @property
    def ControlSocket(self) -> iControlSocket | None: ...

    @property
    def CodecContext(self) -> VideoCodecContext | None: ...
