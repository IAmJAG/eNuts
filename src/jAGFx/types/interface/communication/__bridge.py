# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Mapping, Protocol, runtime_checkable
from uuid import UUID

# ==================================================================================
if TYPE_CHECKING:
    from ....types.interface.communication import iEndpoint, iMessage


# ==================================================================================
@runtime_checkable
class iBridge(Protocol):
    @property
    def messageHandlers(self) -> Mapping[str, Callable[..., Awaitable[None] | None]]: ...

    def attachEndpoint(self, endpoint: iEndpoint) -> None: ...
    def detachEndpoint(self) -> None: ...

    def registerProcessor(
        self,
        correlationId: UUID,
        processor: Callable[[iMessage], Awaitable[None] | None],
    ) -> None: ...

    def unregisterProcessor(self, correlationId: UUID) -> None: ...

    async def handleMessage(self, message: iMessage) -> None: ...


# ==================================================================================
__all__ = ["iBridge"]
