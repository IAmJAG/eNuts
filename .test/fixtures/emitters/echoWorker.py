# ==================================================================================
"""Module-level worker. Spawn imports this. It must not import the emitter."""
# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import to_thread
from multiprocessing import Queue
from multiprocessing.synchronize import Event as syncEvent
from queue import Empty

# ==================================================================================
from fluxCore.emitters.__helper import asyncCloseQueue


# ==================================================================================
async def echoWorker(
    clientId: str,
    shutdownEvent: syncEvent,
    inQueue: Queue,
    outQueue: Queue,
) -> None:
    try:
        while not shutdownEvent.is_set():
            try:
                msg = await to_thread(inQueue.get, True, 0.1)

            except Empty:
                continue

            print(f"CHILD {clientId} got {msg!r}", flush=True)
            outQueue.put(f"{clientId}:{msg}")

    finally:
        await asyncCloseQueue(inQueue)
        await asyncCloseQueue(outQueue)
