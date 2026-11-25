# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Protocol, Union, runtime_checkable

# ==================================================================================
from fluxCore.types.interface.device import iDevice
from jAGFx.types.interface.communication.client import iClient
from jAGFx.types.interface.communication.messages import iMessage


# ==================================================================================
@runtime_checkable
class iDeviceManager(iClient, Protocol):
    def addDevice(self, device: iDevice): ...
    def removeDevice(self, device: Union[str, iDevice]) -> iDevice: ...
    async def processMessage(self, msg: iMessage, handled: bool = False): ...