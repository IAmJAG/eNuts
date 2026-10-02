# ==================================================================================
from typing import Awaitable, Callable, Protocol, runtime_checkable


# ==================================================================================
@runtime_checkable
class iService(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def isRunning(self) -> bool: ...

    work: Callable[..., Awaitable] | None

    def start(self, *args, **kwargs) -> None: ...
    def stop(self, *args, **kwargs) -> None: ...


# ==================================================================================
__all__ = ["iService"]
