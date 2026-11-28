# ==================================================================================
from __future__ import annotations

# ==================================================================================
from collections.abc import Awaitable, Callable
from multiprocessing import Queue
from multiprocessing.synchronize import Event as syncEvent

# ==================================================================================
from fluxCore.types.interface.device import iDevice
from jAGFx.IPC.client import beat, ownDispatch, watcher
from jAGFx.IPC.message import Handshake
from jAGFx.types.interface.communication import iMessage

# ==================================================================================
Handler: type = Callable[[iMessage, syncEvent, Queue], Awaitable]
# ==================================================================================

# ==================================================================================
async def streamStarter(shutdownEvent: syncEvent, inQueue: Queue, outQueue: Queue, messageHandler: Handler, clientId: str| None = None):
    print(f"Starting clientId: {clientId}")
    await watcher(shutdownEvent, inQueue, outQueue, messageHandler)

# ==================================================================================
async def streamerMessageHandler(msg: iMessage, shutdownEvent: syncEvent, outQueue: Queue):
    if isinstance(msg, Handshake):
        verbose(f"Acknowleged [{msg.ownerId}]")
        createTask(beat, shutdownEvent, outQueue)

