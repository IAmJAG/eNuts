# ==================================================================================
from multiprocessing import current_process
from typing import Any, Optional
from uuid import UUID

# ==================================================================================
from jAGFx.types.interface.communication.messages import (
    iHandshake,
    iHandshakeConfirmation,
)

# ==================================================================================
from .__message import G_DEFAULT_MSG_TIMEOUT, Message


# ==================================================================================
class HandshakeConfirmation(iHandshakeConfirmation, Message):
    def __init__(self, handshake: iHandshake) -> None:
        processId = current_process().ident
        super().__init__(
            processId, handshake.correlationId,
            handshake.messageId, processId, True, G_DEFAULT_MSG_TIMEOUT,
        )

    @property
    def processId(self) -> int:
        return self.payload


# ==================================================================================
__all__ = ["HandshakeConfirmation"]