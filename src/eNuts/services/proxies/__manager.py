# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import to_thread
from multiprocessing import Queue, current_process
from multiprocessing.synchronize import Event as syncEvent
from queue import Empty
from typing import Awaitable, Callable, Optional
from uuid import uuid4

# ==================================================================================
from jAGFx.IPC import asyncCloseQueue, asyncDrainQueue
from jAGFx.IPC.message import Handshake, Terminated
from jAGFx.types.interface.communication.messages import iMessage


# ==================================================================================
async def own(msg: iMessage) -> iMessage:
    identity: int = current_process().ident
    msg.messageId = uuid4()
    msg.ownerId = identity
    return msg

# ==================================================================================
async def dispatch(outQueue: Queue, msg: iMessage):
    try:
        outQueue.put(msg)

    except Exception as ex:
        raise

# ==================================================================================
async def ownDispatch(outQueue: Queue, msg: iMessage):
    msg: iMessage = await own(msg)
    await dispatch(outQueue, msg)

# ==================================================================================
async def watcher(
    shutdownEvent: syncEvent,
    messageHandler: Callable[[iMessage, ...], Awaitable],
    inQueue: Queue, outQueue: Queue
):
    def isShuttingdown() -> bool: ...
    isShuttingdown = shutdownEvent.is_set

    try:
        while not isShuttingdown():
            try:
                msg: iMessage = await to_thread(inQueue.get, True, 0.1)
                await messageHandler(msg)

            except Empty:
                continue        

    except BaseException as ex:
        raise ex

    finally:
        await asyncDrainQueue(inQueue)
        await asyncCloseQueue(inQueue)

# ==================================================================================
__all__ = ["own", "ownDispatch", "dispatch", "watcher"]