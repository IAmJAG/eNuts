# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Dict, List, Union

# ==================================================================================
from fluxCore.types.interface.device import iDevice
from jAGFx.IPC.client import Client
from jAGFx.types.interface.communication.messages import iMessage

# ==================================================================================
from ....types.interface.services import iDeviceManager
from .message import DeviceAdded, DeviceListInitialized, DeviceRemoved


# ==================================================================================
class DeviceManager(iDeviceManager, Client):
    def __init__(self, clientId: int):
        super().__init__(clientId=clientId)
        self._devices: Dict[str, iDevice] = dict[str, iDevice]()

    def addDevice(self, device: iDevice):
        self._devices[device.id] = device

    def removeDevice(self, device: Union[str, iDevice]) -> iDevice:
        device: str = device if isinstance(device, str) else device.id
        return self._devices.pop(device, None)

    async def processMessage(self, msg: iMessage, handled: bool = False):
        if handled: return
        
        if isinstance(msg, DeviceListInitialized) and not handled:
            newDevices: List[iDevice] = list(msg.payload.values())
            for device in newDevices: self.addDevice(device)
            self.raiseEvent("DEVICE_LIST_INITIALIZED", newDevices)
            handled = True

        if isinstance(msg, DeviceAdded) and not handled:
            newDevice: iDevice = msg.device
            self.addDevice(newDevice)
            self.raiseEvent("DEVICE_ADDED", newDevice)
            handled = True

        if isinstance(msg, DeviceRemoved) and not handled:
            newDevice: iDevice = msg.device
            self.removeDevice(newDevice)
            self.raiseEvent("DEVICE_REMOVED", newDevice)
            handled = True

        await super().processMessage(msg, handled=handled)