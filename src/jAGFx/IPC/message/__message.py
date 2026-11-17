# ==================================================================================
from time import time
from typing import Optional, Union
from uuid import UUID, uuid4

# ==================================================================================
from jAGFx.serializer import Serializable
from jAGFx.types.interface.serializer import iSerializable

# ==================================================================================
from ...types.interface.communication import iMessage


# ==================================================================================
class Message(iMessage, Serializable):
    def __init__(
        self, payload: Optional[iSerializable],
        correlationId: Optional[UUID], messageId: UUID,  ownerId: Optional[UUID],
        isTerminal: Optional[bool], timestamp: Optional[float],
    ) -> None:
        super().__init__()
        self._correlationId: Optional[UUID] = correlationId or uuid4()
        self._ownerId: Optional[UUID] = ownerId or uuid4()
        self._messageId: Optional[UUID] = messageId or uuid4()

        self._payload: Optional[iSerializable] = payload
        self._isTerminal: Optional[bool] = isTerminal
        self._timestamp: Optional[float] = timestamp or time()

        self.Properties.extend(
            [
                "payload", "timestamp", "isTerminal", 
                "correlationId", "messageId", "ownerId",                
            ]
        )

    @property
    def payload(self) -> iSerializable | None:
        return self._payload

    @payload.setter
    def payload(self, value: iSerializable) -> None:
        self._payload = value

    @property
    def correlationId(self) -> UUID | None:
        return self._correlationId

    @property
    def messageId(self) -> UUID:
        return self._messageId

    @property
    def ownerId(self) -> UUID | None:
        return self._ownerId

    @ownerId.setter
    def ownerId(self, value: UUID | None) -> None:
        self._ownerId = value

    @property
    def timestamp(self) -> float:
        return self._timestamp

    @property
    def isTerminal(self) -> bool:
        return self._isTerminal

# ==================================================================================
__all__ = ["Message"]
