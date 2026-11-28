# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import Task, to_thread
from asyncio import sleep as asyncSleep
from collections.abc import Awaitable, Callable
from multiprocessing import Queue, current_process
from multiprocessing.synchronize import Event as syncEvent
from queue import Empty
from uuid import uuid4

# ==================================================================================
from jAGFx.IPC import asyncCloseQueue, asyncDrainQueue
from jAGFx.IPC.message import Handshake, Heartbeat, Terminate
from jAGFx.types.interface.communication.messages import iMessage

# ==================================================================================
Handler: type = Callable[[iMessage, syncEvent, Queue], Awaitable]
# ==================================================================================

# ==================================================================================
async def _watcher(shutdownEvent: syncEvent, inQueue: Queue, outQueue: Queue, messageHandler: Handler):
    def isShuttingdown() -> bool: ...
    isShuttingdown = shutdownEvent.is_set

    try:
        while not isShuttingdown():
            try:
                msg: iMessage = await to_thread(inQueue.get, True, 0.1)
                await messageHandler(msg, shutdownEvent, outQueue)

            except Empty:
                continue

    finally:
        await asyncDrainQueue(inQueue)
        await asyncCloseQueue(inQueue)

# ==================================================================================
async def watcher(
    shutdownEvent: syncEvent,inQueue: Queue, outQueue: Queue, messageHandler: Handler,
    theWatch: Callable[[...], Awaitable]| None = None,
):
    err: Exception | BaseException | None = None

    try:
        theWatch = theWatch or _watcher
        watcherTask: Task = createTask(theWatch, shutdownEvent, inQueue, outQueue, messageHandler)

        handShake: Handshake = Handshake()
        await ownDispatch(outQueue, handShake)
        await watcherTask

    except BaseException as bex:
        err = bex
        raise

    finally:
        terminated: Terminate = Terminate(error=err)
        await ownDispatch(outQueue, terminated)

# ==================================================================================
async def beat(shutdownEvent: syncEvent, queue: Queue):
    def isShuttingDown() -> bool: ...
    isShuttingDown = shutdownEvent.is_set
    
    BEAT: float = 2.0
    MARGIN: float = 0.2
    INTERVAL: float = max(0.05, BEAT - MARGIN)
    while not isShuttingDown():
        heartbeat: Heartbeat = Heartbeat(BEAT)
        verbose(f"Sending Heartbeat beat={BEAT}")
        await ownDispatch(queue, heartbeat)
        await asyncSleep(INTERVAL)

# ==================================================================================
async def own(msg: iMessage) -> iMessage:
    identity: int = current_process().ident
    msg.messageId = uuid4()
    msg.ownerId = identity
    return msg

# ==================================================================================
async def dispatch(outQueue: Queue, msg: iMessage):
    outQueue.put(msg)

# ==================================================================================
async def ownDispatch(outQueue: Queue, msg: iMessage):
    msg: iMessage = await own(msg)
    await dispatch(outQueue, msg)

# ==================================================================================
__all__ = ["dispatch", "own", "ownDispatch", "watcher"]
