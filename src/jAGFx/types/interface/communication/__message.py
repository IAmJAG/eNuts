# ==================================================================================
from typing import Protocol, runtime_checkable
from uuid import UUID

# ==================================================================================
from ..serializer import iSerializable


# ==================================================================================
@runtime_checkable
class iMessage(iSerializable, Protocol):
    @property
    def payload(self) -> iSerializable: ...

    @property
    def correlationId(self) -> UUID: ...

    @property
    def messageId(self) -> UUID: ...

__all__ = ["iMessage"]
