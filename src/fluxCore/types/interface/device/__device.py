# ==================================================================================
from typing import Protocol, runtime_checkable

# ==================================================================================
from jAGFx.types.interface.serializer import iSerializable


# ==================================================================================
@runtime_checkable
class iDevice(iSerializable, Protocol):
    def __init__(self, id: str) -> None: ...
    @property 
    def id(self) -> str: ...
    @property
    def name(self) -> str | None: ...
    