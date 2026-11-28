# ==================================================================================
from __future__ import annotations

# ==================================================================================
from collections.abc import Awaitable, Callable
from multiprocessing import Queue
from multiprocessing.synchronize import Event as syncEvent
from typing import Protocol, runtime_checkable

# ==================================================================================
from ....globals.services import C_DEFAULT_STOP_TIMEOUT
from ..services import iService
from .client import iClient
from .messages import iMessage

# ==================================================================================
Handler: type = Callable[[iMessage, syncEvent, Queue], Awaitable]
# ==================================================================================

# ==================================================================================
@runtime_checkable
class iProcessHost(iService, Protocol):
    @property
    def clients(self) -> dict[int, iClient]: ...
    def running(self, clientId: int | None = None) -> bool: ...
    def start(self, worker: Callable[..., Awaitable],clientType: iClient, handler: Handler, *args, **kwargs) -> iClient: ...
    def stop(self, timeout: float = C_DEFAULT_STOP_TIMEOUT, forced: bool = False) -> None: ...

# ==================================================================================
__all__ = ["iProcessHost"]

