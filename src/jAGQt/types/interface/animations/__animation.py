# ==================================================================================
# src/jAGQt/types/interface/animations/__animation.py
# ==================================================================================
from typing import Protocol, runtime_checkable


# ==================================================================================
@runtime_checkable
class iAnimation(Protocol):
    """Contract for jAGQt custom animations (property, icon morph, etc.)."""

    @property
    def isRunning(self) -> bool: ...

    @property
    def durationMs(self) -> int: ...

    def start(self) -> None: ...

    def stop(self) -> None: ...
