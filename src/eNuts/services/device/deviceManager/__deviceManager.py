# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import to_thread
from multiprocessing import Queue, current_process
from multiprocessing.synchronize import Event as syncEvent
from queue import Empty
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
async def _watcher(shutdownEvent: syncEvent, queue: Queue):
    def isShuttingdown() -> bool: ...
    isShuttingdown = shutdownEvent.is_set

    try:    
        while not isShuttingdown():            
            try:                    
                msg: iMessage = queue.get_nowait(0.1)
                print(f"Watchign payload: {msg.payload}")

            except Empty:
                
                continue

    except Exception:
        raise

    finally:
        # Ensure shutdown event is set/triggered
        if not isShuttingdown(): shutdownEvent.set()
        await asyncDrainQueue(queue)
        await asyncCloseQueue(queue)

# ==================================================================================
async def deviceWatcher(shutdownEvent: syncEvent, inQueue: Queue, outQueue: Queue):
    createTask(_watcher, shutdownEvent, inQueue)
    handShake: Handshake = Handshake(correlationId=uuid4(), messageId=uuid4())
    await dispatch(outQueue, handShake)
