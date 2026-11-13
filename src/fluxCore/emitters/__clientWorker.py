# ==================================================================================
"""Child entry for outOfProcessEmitter.

This module must not import the emitter. Spawn imports this function by name.
A method or a nested function cannot be the process target.
"""
# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import to_thread
from multiprocessing import Queue
from multiprocessing.synchronize import Event as syncEvent
from queue import Empty

# ==================================================================================
from .__helper import asyncCloseQueue


# ==================================================================================
async def _clientWorker(
    clientId: str,
    shutdownEvent: syncEvent,
    inQueue: Queue,
    outQueue: Queue,
) -> None:
    """Read this client's inbound queue. Write the shared outbound queue.

    inQueue is the parent's dedicated outbound to this client.
    outQueue is the parent's single inbound, shared by every client.
    """
    try:
        while not shutdownEvent.is_set():
            try:
                lMsg = await to_thread(inQueue.get, True, 0.1)

            except Empty:
                continue

            print(f"[{clientId}] {lMsg}")

    finally:
        await asyncCloseQueue(inQueue)
        await asyncCloseQueue(outQueue)


# ==================================================================================
__all__ = ["_clientWorker"]
