# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import TYPE_CHECKING, Protocol, runtime_checkable

# ==================================================================================
if TYPE_CHECKING:
    from ....types.interface.communication import iMessage


# ==================================================================================
@runtime_checkable
class iEndpoint(Protocol):
    async def start(self) -> None: ...
    async def stop(self) -> None: ...
    async def send(self, message: iMessage) -> None: ...


# ==================================================================================
__all__ = ["iEndpoint"]
