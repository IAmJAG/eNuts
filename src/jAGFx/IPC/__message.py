# ==================================================================================
from time import time
from uuid import UUID, uuid4

# ==================================================================================
from jAGFx.serializer import Serializable
from jAGFx.types.interface.serializer import iSerializable

# ==================================================================================
from ..types.interface.communication import iMessage


# ==================================================================================
class Message(iMessage, Serializable):
    def __init__(
        self,
        payload: iSerializable,
        correlationId: UUID | None = None,
        isTerminal: bool = False,
        timestamp: float | None = None,
    ) -> None:
        super().__init__()
        self._payload: iSerializable = payload
        self._correlationId: UUID | None = correlationId or uuid4()
        self._messageId: UUID = uuid4()
        self._isTerminal: bool = isTerminal
        self._timestamp: float = timestamp if timestamp is not None else time()
        self.Properties.extend(
            ["payload", "correlationId", "messageId", "timestamp", "isTerminal"]
        )

    @property
    def payload(self) -> iSerializable:
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
    def timestamp(self) -> float:
        return self._timestamp

    @property
    def isTerminal(self) -> bool:
        return self._isTerminal


__all__ = ["Message"]
