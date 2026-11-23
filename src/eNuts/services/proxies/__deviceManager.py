# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import Task, to_thread
from multiprocessing import Queue, current_process
from multiprocessing.synchronize import Event as syncEvent
from queue import Empty
from typing import Optional
from uuid import uuid4

# ==================================================================================
from jAGFx.IPC import asyncCloseQueue, asyncDrainQueue
from jAGFx.IPC.message import Handshake
from jAGFx.types.interface.communication.messages import iMessage


# ==================================================================================
async def dispatch(outQueue: Queue, msg: iMessage):
    try:
        identity: int = current_process().ident
        msg.messageId = uuid4()
        msg.ownerId = identity

        outQueue.put(msg)

    except Exception as ex:
        raise

# ==================================================================================
async def _watcher(shutdownEvent: syncEvent, inQueue: Queue, outQueue: Queue):
    def isShuttingdown() -> bool: ...
    isShuttingdown = shutdownEvent.is_set

    err: Optional[Exception] = None

    try:
        while not isShuttingdown():
            try:
                msg: iMessage = await to_thread(inQueue.get, True, 0.1)
                if isinstance(msg, Handshake):
                    trace(f"Acknowleged {msg.ownerId}")

            except Empty:
                continue        

    except BaseException as ex:
        err = ex
        raise

    finally:
        if not isShuttingdown(): shutdownEvent.set()        
        await asyncDrainQueue(inQueue)
        await asyncCloseQueue(inQueue)

# ==================================================================================
async def deviceWatcher(shutdownEvent: syncEvent, inQueue: Queue, outQueue: Queue):
    watcher: Task = createTask(_watcher, shutdownEvent, inQueue, outQueue)
    watcher.add_done_callback(logTaskException)

    handShake: Handshake = Handshake(correlationId=uuid4(), messageId=uuid4())
    await dispatch(outQueue, handShake)
    await watcher
