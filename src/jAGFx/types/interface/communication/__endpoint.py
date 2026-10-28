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
    async def stop(self, *, drainTimeout: float = 1.0) -> None: ...
    async def send(self, message: iMessage) -> None: ...

    def registerBridge(self, bridge: iBridge, *, asDefault: bool = False) -> None: ...
    def unregisterBridge(self, bridge: iBridge) -> None: ...

    @property
    def defaultBridgeId(self) -> UUID | None: ...

    def markBridgeAlive(self, bridgeId: UUID, ttlS: float) -> None: ...
    def isBridgeAlive(self, bridgeId: UUID) -> bool: ...
    def sweepDeadBridges(self) -> list[UUID]: ...


# ==================================================================================
__all__ = ["iEndpoint"]
