# ==================================================================================
from multiprocessing import current_process
from typing import Any, Optional
from uuid import UUID

# ==================================================================================
from jAGFx.types.interface.communication.messages import iHandshake

# ==================================================================================
from .__message import G_DEFAULT_MSG_TIMEOUT, Message


# ==================================================================================
class Handshake(iHandshake, Message):
    def __init__(
        self,
        correlationId: Optional[UUID | Any] = None, messageId: Optional[UUID] = None,
        ownerId: Optional[UUID]  = None, timestamp: Optional[float] = G_DEFAULT_MSG_TIMEOUT,
    ) -> None:
        processId = current_process().ident
        super().__init__(processId, correlationId, messageId, ownerId, True, timestamp)

    @property
    def processId(self) -> int:
        return self.payload


# ==================================================================================
__all__ = ["Handshake"]