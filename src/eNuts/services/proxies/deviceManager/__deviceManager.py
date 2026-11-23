# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import Task
from multiprocessing import Queue
from multiprocessing.synchronize import Event as syncEvent
from uuid import uuid4

# ==================================================================================
from jAGFx.IPC.message import Handshake

# ==================================================================================
from ..__manager import ownDispatch, watcher


# ==================================================================================
async def deviceWatcher(shutdownEvent: syncEvent, inQueue: Queue, outQueue: Queue):
    watcherTask: Task = createTask(watcher, shutdownEvent, inQueue, outQueue)
    watcherTask.add_done_callback(logTaskException)

    handShake: Handshake = Handshake(correlationId=uuid4(), messageId=uuid4())
    await ownDispatch(outQueue, handShake)
    await watcherTask
