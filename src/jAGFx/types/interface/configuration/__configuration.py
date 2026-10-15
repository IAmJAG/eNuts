# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Protocol, runtime_checkable

# ==================================================================================
from ..serializer import iSerializable


# ==================================================================================
@runtime_checkable
class iConfiguration(iSerializable, Protocol):
    @property
    def sections(self) -> iConfiguration: ...
    def load(self, path: str) -> iConfiguration: ...    
    def save(self, path: str = None) -> iConfiguration: ...
        