# ==================================================================================
from typing import Protocol, runtime_checkable


# ==================================================================================
@runtime_checkable
class iAnimation(Protocol):
    """Contract for jAGQt custom animations (property, wipe, etc.)."""

    @property
    def isRunning(self) -> bool: ...

    @property
    def durationMs(self) -> int: ...

    def start(self, *args, **kwargs) -> None: ...

    def stop(self) -> None: ...
