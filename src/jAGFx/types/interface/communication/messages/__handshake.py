# ==================================================================================
from .__message import iMessage


# ==================================================================================
class iHandshake(iMessage):
    @property
    def processId(self) -> int: ...
        

__all__ = ["iHandshake"]
