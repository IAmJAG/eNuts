# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Protocol, runtime_checkable

# ==================================================================================
from jAGFx.types.interface.serializer import iSerializable


# ==================================================================================
@runtime_checkable
class iEmbeddingItem(iSerializable, Protocol):
    def __init__(self, key: str, description: str): ...

    @property
    def key(self) -> str: ...
    @property
    def description(self) -> str: ...
