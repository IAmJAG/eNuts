# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Any, Protocol, runtime_checkable

# ==================================================================================
from jAGFx.types.interface.services import iService

# ==================================================================================
from .frameRing import iFrameRing


# ==================================================================================
@runtime_checkable
class iFrameConsumer(iService, Protocol):
    def attachRing(self, ring: iFrameRing) -> None: ...
    def detachRing(self) -> None: ...
