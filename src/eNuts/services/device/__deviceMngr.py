# ==================================================================================
from __future__ import annotations

# ==================================================================================
from multiprocessing import Queue, current_process
from multiprocessing.synchronize import Event as syncEvent
from typing import Awaitable, Callable, Dict, Type
from uuid import uuid4

# ==================================================================================
from jAGFx.IPC.message import Handshake
from jAGFx.types.interface.communication.messages import iMessage


# ==================================================================================
async def dispatch(outQueue: Queue, msg: iMessage):
    try:
        identity: int = current_process().ident
        msg.messageId = uuid4()
        msg.ownerId = identity

        outQueue.put(msg)

    except Exception as ex:
        raise

async def defaultMessageHandler(msg: iMessage):     
    processId = current_process().ident
    trace(f"[{processId}] Message received from {msg.ownerId}: [{type(msg).__name__}] [{msg.payload}]")

async def handshakeHandler(msg: iMessage):
    processId = current_process().ident
    trace(f"[{processId}] Handshake message received from {msg.ownerId}: [{type(msg).__name__}] [{msg.payload}]")

async def handshakeConfirmHandler(msg: iMessage): 
    processId = current_process().ident
    trace(f"[{processId}] Handshake confirmation message received from {msg.ownerId}: [{type(msg).__name__}] [{msg.payload}]")

# ==================================================================================
async def deviceWatcher(shutdownEvent: syncEvent, inQueue: Queue, outQueue: Queue):
    handlers: Dict[Type, Callable[[iMessage], Awaitable]] = {
        Handshake: handshakeHandler,
    }

    handShake: Handshake = Handshake(correlationId=uuid4(), messageId=uuid4())
    await dispatch(outQueue, handShake)
