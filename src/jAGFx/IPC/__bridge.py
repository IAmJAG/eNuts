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

    Subclasses populate messageHandlers and implement domain behavior.
    Kind strings are open-ended; define them per concrete bridge.
    """

    def __init__(self) -> None:
        self._endpoint: iEndpoint | None = None
        self._processors: Dict[UUID, Callable[[iMessage], Awaitable[...]]] = {}
        self._messageHandlers: Dict[Type[iMessage], Callable[[iMessage], Awaitable[...]]] = {}

    @property
    def messageHandlers(self) -> Mapping[Type[iMessage], Callable[[iMessage], Awaitable[...]]]:
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
        processor: Callable[[UUID], Awaitable[None] | None],
    ) -> None:
        self._processors[correlationId] = processor

    def unregisterProcessor(self, correlationId: UUID) -> None:
        self._processors.pop(correlationId, None)

    async def handleMessage(self, message: iMessage) -> None:
        processor = self._processors.get(message.correlationId)
        if processor is not None:
            result = processor(message)
            if result is not None: await result
            return

        kind = type(message)
        handler = self._messageHandlers.get(kind, None) if kind is not None else None
        if handler is None: return

        result = handler(message)
        if result is not None: await result    

    async def send(self, message: iMessage) -> None:
        if self._endpoint is None:
            raise RuntimeError("Bridge has no attached Endpoint")
        
        await self._endpoint.send(message)


# ==================================================================================
__all__ = ["Bridge"]
