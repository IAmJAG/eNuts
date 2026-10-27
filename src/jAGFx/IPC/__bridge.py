# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Awaitable, Callable, Dict, Mapping, Type
from uuid import UUID

# ==================================================================================
from ..types.interface.communication import iBridge, iEndpoint, iMessage


# ==================================================================================
class Bridge(iBridge):
    """Process-local base for entity binding (real or proxy role).

    Subclasses populate messageHandlers keyed by message type and implement
    domain behavior. Concrete bridges may subclass Message for distinct kinds.
    """

    def __init__(self) -> None:
        self._endpoint: iEndpoint | None = None
        self._processors: Dict[UUID, Callable[[iMessage], Awaitable[None] | None]] = {}
        self._messageHandlers: Dict[
            Type[iMessage], Callable[[iMessage], Awaitable[None] | None]
        ] = {}

    @property
    def messageHandlers(
        self,
    ) -> Mapping[Type[iMessage], Callable[[iMessage], Awaitable[None] | None]]:
        return self._messageHandlers

    @property
    def endpoint(self) -> iEndpoint | None:
        return self._endpoint

    def attachEndpoint(self, endpoint: iEndpoint) -> None:
        self._endpoint = endpoint

    def detachEndpoint(self) -> None:
        self._endpoint = None
        self._processors.clear()

    def registerProcessor(
        self,
        correlationId: UUID,
        processor: Callable[[iMessage], Awaitable[None] | None],
    ) -> None:
        self._processors[correlationId] = processor

    def unregisterProcessor(self, correlationId: UUID) -> None:
        self._processors.pop(correlationId, None)

    def hasProcessor(self, correlationId: UUID) -> bool:
        return correlationId in self._processors

    async def handleMessage(self, message: iMessage) -> None:
        processor = self._processors.get(message.correlationId)
        if processor is not None:
            result = processor(message)
            if result is not None:
                await result
            return

        handler = self._messageHandlers.get(type(message))
        if handler is None:
            return

        result = handler(message)
        if result is not None:
            await result

    async def send(self, message: iMessage) -> None:
        if self._endpoint is None:
            raise RuntimeError("Bridge has no attached Endpoint")

        await self._endpoint.send(message)


# ==================================================================================
__all__ = ["Bridge"]
