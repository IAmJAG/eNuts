# ==================================================================================
from time import monotonic_ns
from typing import Optional, Union
from uuid import UUID, uuid4

# ==================================================================================
from jAGFx.serializer import Serializable
from jAGFx.types.interface.serializer import iSerializable

# ==================================================================================
from ...types.interface.communication import iMessage

# ==================================================================================
G_DEFAULT_MSG_TIMEOUT: float = 0.5 # seconds
# ==================================================================================

# ==================================================================================
class Message(iMessage, Serializable):
    def __init__(
        self, ownerId: Optional[Union[UUID, str]],
        payload: Optional[iSerializable],        
        correlationId: Optional[UUID], messageId: UUID,
        isTerminal: Optional[bool],
    ) -> None:
        super().__init__()
        self._ownerId: Union[UUID, str] = ownerId
        self._payload: Optional[iSerializable] = payload

        self._correlationId: Optional[UUID] = correlationId or uuid4()        
        self._messageId: Optional[UUID] = messageId or uuid4()

        self._isTerminal: Optional[bool] = isTerminal        
        self._timestamp: int = monotonic_ns()

        self.Properties.extend(
            [
                "ownerId",
                "payload",  

                "correlationId",
                "messageId",
                
                "isTerminal",
                "timestamp",
            ]
        )

    @property
    def payload(self) -> Optional[iSerializable]:
        return self._payload

    @payload.setter
    def payload(self, value: Optional[iSerializable]) -> None:
        self._payload = value

    @property
    def correlationId(self) -> Optional[UUID]: 
        return self._correlationId

    @property
    def messageId(self) -> UUID: 
        return self._messageId

    @property
    def ownerId(self) -> Union[UUID, str]: 
        return self._ownerId

    @property
    def timestamp(self) -> int: 
        return self._timestamp

    @property
    def isTerminal(self) -> bool: 
        return self._isTerminal

# ==================================================================================
__all__ = ["Message"]
