# ==================================================================================
from multiprocessing import current_process
from typing import Optional
from uuid import UUID

# ==================================================================================
from .__message import Message


# ==================================================================================
class Terminated(Message):    
    def __init__(
        self,        
        correlationId: Optional[UUID] = None, messageId: UUID = None,
        isTerminal: Optional[bool] = False,
        error: Optional[BaseException] = None,
    ) -> None:
        processId = current_process().ident
        super().__init__(
            ownerId=processId, payload=error, correlationId=correlationId,
            messageId=messageId, isTerminal=isTerminal
        )
        
# ==================================================================================
__all__ = ["Terminated"]