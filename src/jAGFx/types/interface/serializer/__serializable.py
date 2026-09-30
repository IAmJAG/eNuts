# ==================================================================================
# src/jAGFx/types/interface/serializer/__serializeable.py
# ==================================================================================
from typing import Protocol, runtime_checkable


# ==================================================================================
@runtime_checkable
class iSerializable(Protocol):
    @property
    def Properties(cls) -> list[str]: ...
    def encode(cls) -> dict[str, object]: ...    
    def decode(cls, dct: dict[str, object]): ...
