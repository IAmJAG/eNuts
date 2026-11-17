# ==================================================================================
from typing import Optional
from uuid import UUID

# ==================================================================================
from .__message import Message


# ==================================================================================
class Handshake(Message):
    def __init__(
        self, payload: Optional[str] = None, 
        correlationId: Optional[UUID] = None, messageId: Optional[UUID] = None,
        ownerId: Optional[UUID]  = None, 
        isTerminal: Optional[bool] = False, timestamp: Optional[float] = 0.01,
    ) -> None:
        super().__init__(payload, correlationId, messageId, ownerId, isTerminal, timestamp)

# ==================================================================================
__all__ = ["Handshake"]