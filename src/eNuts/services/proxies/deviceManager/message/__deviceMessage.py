# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Dict, Optional, Union
from uuid import UUID

# ==================================================================================
from fluxCore.types.interface.device import iDevice
from jAGFx.IPC.message import Message


# ==================================================================================
class OnDevice(Message):
    def __init__(
        self, ownerId: Optional[Union[UUID, str]] = None,
        devices: Optional[iDevice] = None, correlationId: Optional[UUID] = None,
        messageId: UUID = None, isTerminal: Optional[bool] = True,
    ) -> None:
        super().__init__(
            ownerId=ownerId, payload=devices,
            correlationId=correlationId, messageId=messageId,
            isTerminal=isTerminal
        )

    @property
    def devices(self) -> Union[Dict[str, iDevice], iDevice]: 
        return self.payload