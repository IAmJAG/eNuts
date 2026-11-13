# ==================================================================================
"""Module-level worker. Spawn imports this. It must not import the emitter.

trace is the logging builtin from src/__monkeyPatch.py, declared in
typings/__builtins__.pyi. The child imports the patch so trace exists here.
"""
# ==================================================================================
from __future__ import annotations

# ==================================================================================
import importlib
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
    # Own module, not a method: the leading double underscore is not mangled.
    importlib.import_module("__monkeyPatch")
    setupLogging("echoWorker")

    try:
        while not shutdownEvent.is_set():
            try:
                msg = await to_thread(inQueue.get, True, 0.1)

            except Empty:
                continue

            trace(f"FLOW  client {clientId} inbound got {msg!r}")
            reply = f"{clientId}:{msg}"
            outQueue.put(reply)
            trace(f"FLOW  client {clientId} outbound put {reply!r}")

    finally:
        await asyncCloseQueue(inQueue)
