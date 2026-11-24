# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Protocol, runtime_checkable

# ==================================================================================
from ....__eClientState import eClientState
from ...services import iSubscription


# ==================================================================================
@runtime_checkable
class iClient(iSubscription, Protocol):
    def beat(self, expiry: float = 0.1) -> None: ...
    @property
    def clientState(self) -> eClientState: ...        
    @property
    def identity(self) -> int: ...
    @property
    def expiry(self) -> int: ...
