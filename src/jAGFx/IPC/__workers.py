# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import to_thread
from multiprocessing import Queue
from multiprocessing.synchronize import Event as syncEvent
from queue import Empty

# ==================================================================================
from adbutils import AdbDevice, adb

# ==================================================================================
from .__helper import asyncCloseQueue


# ==================================================================================
async def SCRCPYWorker(
    clientId: str,
    shutdownEvent: syncEvent,
    inQueue: Queue,
    outQueue: Queue,
    *args,
    **kwargs,
):
    """Domain worker for SCRCPY serial sessions. Not the ProcessHost default."""
    device: AdbDevice = await to_thread(adb.device, serial=clientId)

    def isShuttingdown() -> bool: ...
    isShuttingdown = shutdownEvent.is_set

    while not isShuttingdown():
        try:
            lMsg = await to_thread(inQueue.get, True, 0.1)

        except Empty:
            continue

        print(f"[{clientId}] {lMsg}")


# ==================================================================================
async def _clientWorker(
    clientId: str,
    shutdownEvent: syncEvent,
    inQueue: Queue,
    outQueue: Queue,
    *args,
    **kwargs,
):
    """
    DEFAULT/DUMMY client worker. Replace with a real module-level worker.

    inQueue is the parent's dedicated outbound to this client.
    outQueue is the parent's single inbound, shared by every client.
    Only the dedicated inbound is closed here. The parent closes the shared queue.
    """
    try:
        def isShuttingdown() -> bool: ...
        isShuttingdown = shutdownEvent.is_set
        while not isShuttingdown():
            try:
                lMsg = await to_thread(inQueue.get, True, 0.1)

            except Empty:
                continue

            print(f"[{clientId}] {lMsg}")

    finally:
        await asyncCloseQueue(inQueue)


# ==================================================================================
async def echoWorker(
    clientId: str,
    shutdownEvent: syncEvent,
    inQueue: Queue,
    outQueue: Queue,
    *args,
    **kwargs,
):
    """Smoke / acceptance worker: echoes messages back to the parent."""
    trace(f"FLOW  client {clientId} worker started")
    try:
        def isShuttingdown() -> bool: ...
        isShuttingdown = shutdownEvent.is_set

        while not isShuttingdown():
            try:
                msg = await to_thread(inQueue.get, True, 0.1)

            except Empty:
                continue

            reply = f"FROM {clientId}:{msg}"

            await to_thread(outQueue.put, reply)
            trace(f"FLOW  client {clientId} outbound put {reply!r}")

    finally:
        trace(f"FLOW  client {clientId} worker exiting")
        await asyncCloseQueue(inQueue)


# ==================================================================================
__all__ = ["_clientWorker", "SCRCPYWorker", "echoWorker"]
