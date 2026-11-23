# ==================================================================================
from typing import Optional, Protocol, Union, runtime_checkable
from uuid import UUID

# ==================================================================================
from ...serializer import iSerializable


# ==================================================================================
@runtime_checkable
class iMessage(iSerializable, Protocol):
    @property
    def payload(self) -> Optional[iSerializable]: ...
    @property
    def correlationId(self) -> Optional[UUID]: ...
    @property
    def messageId(self) -> UUID: ...
    @property
    def ownerId(self) -> Union[UUID, str]: ...
    @property
    def timestamp(self) -> int:  ...
    @property
    def isTerminal(self) -> bool:  ...

__all__ = ["iMessage"]
