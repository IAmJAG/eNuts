# ==================================================================================
from typing import Protocol, runtime_checkable
from uuid import UUID

# ==================================================================================
from jAGFx.types.interface.serializer import iSerializable


# ==================================================================================
@runtime_checkable
class iDevice(iSerializable, Protocol):
    def __init__(self, ident: str | UUID  | None = None) -> None: ...
    @property 
    def id(self) -> str: ...
    @property
    def name(self) -> str | None: ...
    