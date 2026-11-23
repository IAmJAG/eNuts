# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Protocol, runtime_checkable


# ==================================================================================
@runtime_checkable
class iProxy(Protocol):
    @property
    def Identity(self) -> int: ...

