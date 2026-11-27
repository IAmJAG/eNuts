# ==================================================================================
from __future__ import annotations

# ==================================================================================
from collections.abc import Awaitable, Callable
from typing import Protocol, runtime_checkable

# ==================================================================================
from ....services import C_DEFAULT_STOP_TIMEOUT
from ....types.interface.services import iService
from .client import iClient


# ==================================================================================
@runtime_checkable
class iProcessHost(iService, Protocol):
    @property
    def clients(self) -> dict[int, iClient]: ...

    async def stopAsync(self, timeout: float = C_DEFAULT_STOP_TIMEOUT, forced: bool = False) -> None: ...
    async def waitStopped(self) -> None: ...

    def start(
        self,
        worker: Callable[..., Awaitable],
        clientType: type[iClient],
        handler: object,
    ) -> iClient: ...

    def running(self, clientId: int | None = None) -> bool: ...
    def stop(self, timeout: float = C_DEFAULT_STOP_TIMEOUT, forced: bool = False) -> None: ...

# ==================================================================================
__all__ = ["iProcessHost"]
