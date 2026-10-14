# ==================================================================================
from uuid import UUID, uuid4

# ==================================================================================
from jAGFx.serializer import Serializable
from jAGFx.types.interface.serializer import iSerializable

# ==================================================================================
from ..types.interface.communication import iMessage


# ==================================================================================
class Message(Serializable, iMessage):
    def __init__(self, payload: iSerializable, correlationId: UUID | None = None) -> None:
        super().__init__()
        self._payload: iSerializable = payload
        self._correlationId: UUID | None = correlationId or uuid4()
        self._messageId: UUID = uuid4()
        self.Properties.extend(["payload", "correlationId", "messageId"])

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


__all__ = ["Message"]
