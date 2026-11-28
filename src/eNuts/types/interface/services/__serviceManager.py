# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Protocol, runtime_checkable

# ==================================================================================
from jAGFx.types.interface.communication.messages import iMessage


# ==================================================================================
@runtime_checkable
class iServiceManager(Protocol):
    async def processMessage(self, message: iMessage, handled: bool = False): ...