# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import to_thread
from multiprocessing import Queue, current_process
from multiprocessing.synchronize import Event as syncEvent
from queue import Empty
from sys import stderr
from uuid import uuid4

# ==================================================================================
from jAGFx.IPC import asyncCloseQueue, asyncDrainQueue
from jAGFx.IPC.message import Handshake
from jAGFx.logging import TRACE, setupLogging
from jAGFx.types.interface.communication.messages import iMessage


def _p(msg: str) -> None:
    print(f"[CHILD] {msg}", file=stderr, flush=True)


# ==================================================================================
async def dispatch(outQueue: Queue, msg: iMessage):
    try:
        identity: int = current_process().ident
        msg.messageId = uuid4()
        msg.ownerId = identity

        outQueue.put(msg)
        _p(f"dispatch put {type(msg).__name__} owner={identity}")
        trace(f"FLOW  dispatch put {type(msg).__name__} owner={identity}")

    except Exception as ex:
        _p(f"dispatch failed: {ex!r}")
        raise

# ==================================================================================
async def _watcher(shutdownEvent: syncEvent, queue: Queue):
    def isShuttingdown() -> bool: ...
    isShuttingdown = shutdownEvent.is_set

    _p(f"_watcher started type={type(queue).__name__} id={id(queue)}")
    try:
        while not isShuttingdown():
            try:
                msg: iMessage = await to_thread(queue.get, True, 0.1)
                _p(f"_watcher received {type(msg).__name__} payload={msg.payload!r}")
                trace(
                    f"FLOW  _watcher received {type(msg).__name__} "
                    f"payload={msg.payload!r} owner={msg.ownerId}"
                )

            except Empty:
                continue

    except Exception as ex:
        _p(f"_watcher error: {ex!r}")
        raise

    finally:
        _p("_watcher exiting")
        if not isShuttingdown():
            shutdownEvent.set()
        await asyncDrainQueue(queue)
        await asyncCloseQueue(queue)

# ==================================================================================
async def deviceWatcher(shutdownEvent: syncEvent, inQueue: Queue, outQueue: Queue):
    setupLogging("deviceWatcher", TRACE)

    _p(
        f"deviceWatcher starting pid={current_process().ident} "
        f"in={type(inQueue).__name__} out={type(outQueue).__name__}"
    )

    watcher = createTask(_watcher, shutdownEvent, inQueue)
    watcher.add_done_callback(logTaskException)

    handShake: Handshake = Handshake(correlationId=uuid4(), messageId=uuid4())
    await dispatch(outQueue, handShake)
    _p("deviceWatcher handshake dispatched")

    # Keep process alive so _watcher can receive the reply
    await watcher
