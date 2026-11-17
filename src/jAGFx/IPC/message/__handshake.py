# ==================================================================================
from typing import Optional
from uuid import UUID

# ==================================================================================
from .__message import Message


# ==================================================================================
class Handshake(Message):
    def __init__(
        self, payload: Optional[str], 
        correlationId: Optional[UUID], messageId: Optional[UUID], ownerId: Optional[UUID], 
        isTerminal: Optional[bool], timestamp: Optional[float],
    ) -> None:
        super().__init__(payload, correlationId, messageId, ownerId, isTerminal, timestamp)

# ==================================================================================
__all__ = ["Handshake"]