# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import TYPE_CHECKING, Any

# ==================================================================================
if TYPE_CHECKING:
    from multiprocessing import Queue

    from ....types.interface.communication import iMessage


# ==================================================================================
class iIOQueue:
    @classmethod
    def createPair(cls) -> tuple[Queue, Queue]: ...
    def send(self, message: iMessage) -> None: ...
    def receive(self, timeout: float | None = None) -> Any: ...
    def close(self) -> None: ...
    def cancelJoinThread(self) -> None: ...

# ==================================================================================
__all__ = ["iIOQueue"]
