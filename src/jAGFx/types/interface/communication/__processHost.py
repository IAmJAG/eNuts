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
from jAGFx.services import C_DEFAULT_STOP_TIMEOUT
from jAGFx.types.interface.services import iService

# ==================================================================================
from .__proxy import iProxy


# ==================================================================================
@runtime_checkable
class iProcessHost(iService, Protocol):
    @property
    def processes(self) -> Dict[int, Process]: ...

    async def stopAsync(self, timeout: float = C_DEFAULT_STOP_TIMEOUT, forced: bool = False) -> None: ...
    async def waitStopped(self) -> None: ...

    def start(self, worker: Callable[..., Awaitable], proxy: Type[iProxy]) -> None: ...
    def running(self, clientId: str | None = None) -> bool: ...
    def stop(self, timeout: float = C_DEFAULT_STOP_TIMEOUT, forced: bool = False) -> None: ...

# ==================================================================================
__all__ = ["iProcessHost"]
