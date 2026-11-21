# ==================================================================================
from __future__ import annotations

# ==================================================================================
from multiprocessing import current_process
from typing import Awaitable, Callable, Dict, Type

# ==================================================================================
from jAGFx.IPC.message import Handshake
from jAGFx.types.interface.communication.messages import iMessage


# ==================================================================================
async def defaultMessageHandler(msg: iMessage):
    processId = current_process().ident
    trace(
        f"[{processId}] Message received from {msg.ownerId}: [{type(msg).__name__}] [{msg.payload}]"
    )

# ==================================================================================
async def handshakeHandler(msg: iMessage):
    processId = current_process().ident
    trace(
        f"[{processId}] Handshake message received from {msg.ownerId}: [{type(msg).__name__}] [{msg.payload}]"
    )

# ==================================================================================
async def handshakeConfirmHandler(msg: iMessage):
    processId = current_process().ident
    trace(
        f"[{processId}] Handshake confirmation message received from {msg.ownerId}: [{type(msg).__name__}] [{msg.payload}]"
    )


# ==================================================================================
handlers: Dict[Type, Callable[[iMessage], Awaitable]] = {
    Handshake: handshakeHandler,
}
# ==================================================================================
