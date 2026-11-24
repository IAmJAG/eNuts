# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Dict, Optional, Union
from uuid import UUID

# ==================================================================================
from fluxCore.types.interface.device import iDevice
from jAGFx.IPC.message import Message


# ==================================================================================
class DeviceDiscoveryEnded(Message):
    def __init__(
        self,
        ownerId: Optional[Union[UUID, str]] = None,
        correlationId: Optional[UUID] = None,
        messageId: UUID = None,
    ) -> None:
        super().__init__(
            ownerId=ownerId,
            payload=None,
            correlationId=correlationId,
            messageId=messageId,
            isTerminal=True,
        )

    @property
    def devices(self) -> Union[Dict[str, iDevice], iDevice]:
        return self.payload
