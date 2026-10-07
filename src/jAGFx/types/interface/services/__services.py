# ==================================================================================
from typing import Protocol, runtime_checkable


# ==================================================================================
@runtime_checkable
class iService(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def isRunning(self) -> bool: ...

    def start(self, *args, **kwargs) -> None: ...
    def stop(self, *args, **kwargs) -> None: ...


# ==================================================================================
__all__ = ["iService"]
