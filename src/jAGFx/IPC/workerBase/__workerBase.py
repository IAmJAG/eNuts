# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import to_thread
from multiprocessing import Queue
from multiprocessing.synchronize import Event as syncEvent
from queue import Empty
from typing import Union
from uuid import UUID

# ==================================================================================
from ...types.interface.communication import iMessage
from ..__helper import asyncCloseQueue
from ..message import Handshake


# ==================================================================================
async def clientWorker(
    clientId: Union[UUID, str], shutdownEvent: syncEvent,
    inQueue: Queue, outQueue: Queue
):
    try:
        def isShuttingdown() -> bool: ...
        isShuttingdown = shutdownEvent.is_set

        outQueue.put(Handshake(clientId))

        while not isShuttingdown():
            try:
                msg: iMessage = await to_thread(inQueue.get, True, 0.1)
                
            except Empty:
                continue

            trace(f"[{clientId}] {msg}")

    finally:
        await asyncCloseQueue(inQueue)
