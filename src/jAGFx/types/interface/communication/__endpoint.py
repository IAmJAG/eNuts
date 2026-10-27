# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import TYPE_CHECKING, Protocol, runtime_checkable
from uuid import UUID

# ==================================================================================
if TYPE_CHECKING:
    from ....types.interface.communication import iBridge, iMessage


# ==================================================================================
@runtime_checkable
class iEndpoint(Protocol):
    async def start(self) -> None: ...
    async def stop(self) -> None: ...
    async def send(self, message: iMessage) -> None: ...

    def registerBridge(self, bridge: iBridge) -> None: ...
    def unregisterBridge(self, bridge: iBridge) -> None: ...
    def bindCorrelation(self, correlationId: UUID, bridge: iBridge) -> None: ...
    def unbindCorrelation(self, correlationId: UUID) -> None: ...


# ==================================================================================
__all__ = ["iEndpoint"]
