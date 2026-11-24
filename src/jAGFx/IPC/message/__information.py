# ==================================================================================
from multiprocessing import current_process
from typing import Optional
from uuid import UUID

# ==================================================================================
from .__message import Message


# ==================================================================================
class Information(Message):
    def __init__(self, message: str, correlationId: Optional[UUID], messageId: UUID) -> None:
        processId = current_process().ident
        super().__init__(
            ownerId=processId,
            payload=message,
            correlationId=correlationId,
            messageId=messageId,
            isTerminal=True,
        )


# ==================================================================================
__all__ = ["Information"]
