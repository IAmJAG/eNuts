# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import TYPE_CHECKING, Awaitable, Callable, Mapping, Protocol, Type, runtime_checkable
from uuid import UUID

# ==================================================================================
if TYPE_CHECKING:
    from ....types.interface.communication import iEndpoint, iMessage


# ==================================================================================
@runtime_checkable
class iBridge(Protocol):
    @property
    def bridgeId(self) -> UUID: ...

    @property
    def messageHandlers(
        self,
    ) -> Mapping[Type[iMessage], Callable[[iMessage], Awaitable[None] | None]]: ...

    def attachEndpoint(self, endpoint: iEndpoint) -> None: ...
    def detachEndpoint(self) -> None: ...

    def registerProcessor(
        self,
        correlationId: UUID,
        processor: Callable[[iMessage], Awaitable[None] | None],
        *,
        activeTimeoutNs: int | None = None,
    ) -> None: ...

    def unregisterProcessor(self, correlationId: UUID) -> None: ...

    def hasProcessor(self, correlationId: UUID) -> bool: ...

    async def handleMessage(self, message: iMessage) -> None: ...


# ==================================================================================
__all__ = ["iBridge"]
