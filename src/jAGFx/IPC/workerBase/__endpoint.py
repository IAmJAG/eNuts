# ==================================================================================
from __future__ import annotations

# ==================================================================================
from multiprocessing import Queue, current_process
from multiprocessing.synchronize import Event as syncEvent
from typing import Awaitable, Callable, Dict, Type
from uuid import uuid4

# ==================================================================================
from jAGFx.IPC.message import Handshake
from jAGFx.types.interface.communication import iEndpoint
from jAGFx.types.interface.communication.messages import iMessage

# ==================================================================================
from .__workerbase import handshakeHandler


# ==================================================================================
class Endpoint(iEndpoint):
    def __init__(self, outQueue: Queue, inQueue: Queue) -> None:
        handlers: Dict[Type, Callable[[iMessage], Awaitable]] = {
            Handshake: handshakeHandler,
        }
        self._handlers: Dict[Type[iMessage], Callable[[iMessage], Awaitable]] = handlers

        self._outQueue: Queue = outQueue
        self._inQueue: Queue = inQueue

# ==================================================================================
    async def dispatch(self, message: iMessage) -> None:
        outQueue: Queue = self._outQueue
        try:
            identity: int = current_process().ident
            message.messageId = uuid4()
            message.ownerId = identity

            outQueue.put(message)
    
        except Exception:
            raise

# ==================================================================================
    async def worker(self, shutdownEvent: syncEvent, inQueue: Queue, outQueue: Queue):
        handShake: Handshake = Handshake(
            correlationId=uuid4(), messageId=uuid4(), isTerminal=True
        )

        self.dispatch(handShake)

# ==================================================================================
__all__ = ["Endpoint"]
