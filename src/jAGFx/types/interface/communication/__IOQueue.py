# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import TYPE_CHECKING, Dict

# ==================================================================================
if TYPE_CHECKING:
    from ....types.interface.communication import iMessage


# ==================================================================================
class iIOQueue:
    @classmethod
    def createPair(cls) -> tuple[iIOQueue, iIOQueue]: ...

    def send(self, message: Dict): ...
    def receive(self) -> iMessage: ...

    def close(self): ...
    def cancelJoinThread(self): ...

# ==================================================================================
__all__ = ["iIOQueue"]
