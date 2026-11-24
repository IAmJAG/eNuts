# ==================================================================================
from __future__ import annotations

# ==================================================================================
from multiprocessing import Process
from typing import (
    Awaitable,
    Callable,
    Dict,
    Protocol,
    Type,
    runtime_checkable,
)

# ==================================================================================
from ....services import C_DEFAULT_STOP_TIMEOUT
from ....types.interface.services import iService
from .client import iClient


# ==================================================================================
@runtime_checkable
class iProcessHost(iService, Protocol):
    @property
    def processes(self) -> Dict[int, Process]: ...

    async def stopAsync(self, timeout: float = C_DEFAULT_STOP_TIMEOUT, forced: bool = False) -> None: ...
    async def waitStopped(self) -> None: ...

    def start(self, worker: Callable[..., Awaitable], proxy: Type[iClient]) -> None: ...
    def running(self, clientId: str | None = None) -> bool: ...
    def stop(self, timeout: float = C_DEFAULT_STOP_TIMEOUT, forced: bool = False) -> None: ...

# ==================================================================================
__all__ = ["iProcessHost"]
