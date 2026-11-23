# ==================================================================================
from multiprocessing import current_process
from typing import Optional
from uuid import UUID

# ==================================================================================
from .__message import Message


# ==================================================================================
class Handshake(Message):    
    def __init__(
        self,
        correlationId: Optional[UUID], messageId: UUID
    ) -> None:
        processId = current_process().ident
        super().__init__(
            ownerId=processId, payload=None, correlationId=correlationId,
            messageId=messageId, isTerminal=True
        )

# ==================================================================================
__all__ = ["Handshake"]