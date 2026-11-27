# ==================================================================================
from multiprocessing import current_process
from typing import Optional
from uuid import UUID

# ==================================================================================
from .__message import Message


# ==================================================================================
class Terminate(Message):    
    def __init__(
        self,        
        correlationId: UUID | None = None, messageId: UUID | None = None,
        isTerminal: bool | None = False,
        error: BaseException | None = None,
    ) -> None:
        processId = current_process().ident
        super().__init__(
            ownerId=processId, payload=error, correlationId=correlationId,
            messageId=messageId, isTerminal=isTerminal
        )
        
# ==================================================================================
__all__ = ["Terminate"]