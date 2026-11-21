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
from jAGFx.logging import TRACE, setupLogging
from jAGFx.types.interface.communication.messages import iMessage


# ==================================================================================
async def dispatch(outQueue: Queue, msg: iMessage):
    try:
        identity: int = current_process().ident
        msg.messageId = uuid4()
        msg.ownerId = identity

        outQueue.put(msg)
        trace(f"FLOW  dispatch put {type(msg).__name__} owner={identity}")

    except Exception as ex:
        trace(f"FLOW  dispatch failed: {ex!r}")
        raise

# ==================================================================================
async def _watcher(shutdownEvent: syncEvent, queue: Queue):
    def isShuttingdown() -> bool: ...
    isShuttingdown = shutdownEvent.is_set

    trace(f"FLOW  _watcher started")
    try:
        while not isShuttingdown():
            try:
                # Queue.get(block=True, timeout=None) — timeout is valid
                msg: iMessage = await to_thread(queue.get, True, 0.1)
                trace(
                    f"FLOW  _watcher received {type(msg).__name__} "
                    f"payload={msg.payload!r} owner={msg.ownerId}"
                )

            except Empty:
                continue

    except Exception as ex:
        trace(f"FLOW  _watcher error: {ex!r}")
        raise

    finally:
        trace("FLOW  _watcher exiting")
        if not isShuttingdown():
            shutdownEvent.set()
        await asyncDrainQueue(queue)
        await asyncCloseQueue(queue)

# ==================================================================================
async def deviceWatcher(shutdownEvent: syncEvent, inQueue: Queue, outQueue: Queue):
    # Child process does not inherit parent logging setup
    setupLogging("deviceWatcher", TRACE)

    trace(f"FLOW  deviceWatcher starting pid={current_process().ident}")
    task = createTask(_watcher, shutdownEvent, inQueue)
    task.add_done_callback(logTaskException)

    handShake: Handshake = Handshake(correlationId=uuid4(), messageId=uuid4())
    await dispatch(outQueue, handShake)
    trace("FLOW  deviceWatcher handshake dispatched")
