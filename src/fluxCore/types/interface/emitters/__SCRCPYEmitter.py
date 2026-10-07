# ==================================================================================
# src/fluxCore/types/interface/emitters/__SCRCPYEmitter.py
# ==================================================================================
from typing import Protocol, runtime_checkable

# ==================================================================================
from jAGFx.types.interface.services import iService, iSubscription

# ==================================================================================
from ..devices import iSCRCPY


# ==================================================================================
@runtime_checkable
class iSCRCPYEmitter(iSCRCPY, iService, iSubscription, Protocol):
    async def initialize(self): ...