# ==================================================================================
"""Module-level worker. Spawn imports this. It must not import the emitter.

The child configures its own root logger because the project's trace() helper
logs through Python's root logger. setupLogging(name) configures a named logger
and, by itself, does not make root-level TRACE messages visible.
"""
# ==================================================================================
from __future__ import annotations

# ==================================================================================
import importlib
import logging
from asyncio import to_thread
from multiprocessing import Queue
from multiprocessing.synchronize import Event as syncEvent
from queue import Empty

# ==================================================================================
from fluxCore.emitters.__helper import asyncCloseQueue


# ==================================================================================
def _setupTraceOutput() -> None:
    """Make TRACE (level 5) visible in this spawned child process."""
    logging.basicConfig(
        level=5,
        format="%(asctime)s [%(levelname)-8s] %(message)s",
        force=True,
    )


# ==================================================================================
async def echoWorker(
    clientId: str,
    shutdownEvent: syncEvent,
    inQueue: Queue,
    outQueue: Queue,
) -> None:
    # Spawn starts a fresh interpreter; install the project's trace builtin.
    importlib.import_module("__monkeyPatch")
    _setupTraceOutput()
    setupLogging("echoWorker")
    trace(f"FLOW  client {clientId} worker started")

    try:
        while not shutdownEvent.is_set():
            try:
                msg = await to_thread(inQueue.get, True, 0.1)

            except Empty:
                continue

            trace(f"FLOW  client {clientId} inbound got {msg!r}")
            reply = f"{clientId}:{msg}"

            # Keep a potentially blocking multiprocessing queue write off the
            # child's asyncio event loop.
            await to_thread(outQueue.put, reply)
            trace(f"FLOW  client {clientId} outbound put {reply!r}")

    finally:
        trace(f"FLOW  client {clientId} worker exiting")
        await asyncCloseQueue(inQueue)


# ==================================================================================
__all__ = ["echoWorker"]
