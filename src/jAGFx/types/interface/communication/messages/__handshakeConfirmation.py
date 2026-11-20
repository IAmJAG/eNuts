# ==================================================================================
from .__message import iMessage


# ==================================================================================
class iHandshakeConfirmation(iMessage):
    @property
    def processId(self) -> int: ...
        

__all__ = ["iHandshakeConfirmation"]
