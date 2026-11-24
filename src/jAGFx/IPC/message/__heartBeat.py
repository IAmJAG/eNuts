# ==================================================================================
from multiprocessing import current_process
from typing import Optional
from uuid import UUID

# ==================================================================================
from .__message import Message


# ==================================================================================
class Heartbeat(Message):
    def __init__(
        self, beat: float = 3.0, correlationId: Optional[UUID] = None, messageId: UUID = None
    ) -> None:
        processId = current_process().ident
        super().__init__(
            ownerId=processId,
            payload=beat,
            correlationId=correlationId,
            messageId=messageId,
            isTerminal=True,
        )


# ==================================================================================
__all__ = ["Heartbeat"]
