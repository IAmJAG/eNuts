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
    """
    queue is a multiprocessing.Queue (parent -> this client).
    get(block=True, timeout=None) is the correct signature.
    """
    def isShuttingdown() -> bool: ...
    isShuttingdown = shutdownEvent.is_set

    trace(f"FLOW  _watcher started type={type(queue).__name__}")
    try:
        while not isShuttingdown():
            try:
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
    """
    Must stay alive; processEntry ends when this coroutine returns.
    inQueue / outQueue are multiprocessing.Queue instances.
    """
    setupLogging("deviceWatcher", TRACE)

    trace(
        f"FLOW  deviceWatcher starting pid={current_process().ident} "
        f"in={type(inQueue).__name__} out={type(outQueue).__name__}"
    )

    watcher = createTask(_watcher, shutdownEvent, inQueue)
    watcher.add_done_callback(logTaskException)

    handShake: Handshake = Handshake(correlationId=uuid4(), messageId=uuid4())
    await dispatch(outQueue, handShake)
    trace("FLOW  deviceWatcher handshake dispatched")

    # Keep the process alive until shutdown so _watcher can receive
    await watcher
