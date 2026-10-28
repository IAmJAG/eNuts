# ==================================================================================
from typing import Protocol, runtime_checkable


# ==================================================================================
@runtime_checkable
class iService(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def isRunning(self) -> bool: ...

    @property
    def throttle(self) -> float: ...

    @throttle.setter
    def throttle(self, value: float) -> None: ...

    def start(self, *args, **kwargs) -> None: ...
    def stop(self, *args, **kwargs) -> None: ...
    def wake(self) -> None: ...


# ==================================================================================
__all__ = ["iService"]
