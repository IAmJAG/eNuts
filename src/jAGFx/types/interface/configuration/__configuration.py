# ==================================================================================
# src/jAGFx/types/interface/configuration/__configuration.py
# ==================================================================================
from typing import Protocol, runtime_checkable


# ==================================================================================
@runtime_checkable
class iConfiguration[T: iConfiguration](Protocol):
    @property
    def sections(self) -> dict[str, T]: ...
    def load(self, path: str) -> T: ...    
    def save(self, path: str = None) -> T: ...
        