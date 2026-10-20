# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Protocol, runtime_checkable

# ==================================================================================
from jAGFx.types.interface.serializer import iSerializable


# ==================================================================================
@runtime_checkable
class iLabel(iSerializable, Protocol):
    @property
    def id(self) -> str: ...
    @property
    def description(self) -> str: ...
