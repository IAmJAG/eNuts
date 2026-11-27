# ==================================================================================
from __future__ import annotations

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
        self._devices: dict[str, iDevice] = dict[str, iDevice]()

    @property
    def devices(self) -> list[iDevice]:
        return list(self._devices.values())

    def addDevice(self, device: iDevice):
        self._devices[device.id] = device

    def removeDevice(self, device: str | iDevice) -> iDevice:
        device: str = device if isinstance(device, str) else device.id
        return self._devices.pop(device, None)

    async def processMessage(self, msg: iMessage, handled: bool = False):        
        if handled: return
        
        if isinstance(msg, DeviceListInitialized) and not handled:
            newDevices: list[iDevice] = list(msg.payload.values())            
            for device in newDevices: self.addDevice(device)
            verbose(f"Initial device list acquired... {self._devices.keys()}")      
            self.raiseEvent("DEVICE_LIST_INITIALIZED", newDevices)
            handled = True

        if isinstance(msg, DeviceAdded) and not handled:
            newDevice: iDevice = msg.device
            verbose(f"Device added id={newDevice.id}")
            self.addDevice(newDevice)
            self.raiseEvent("DEVICE_ADDED", newDevice)
            handled = True

        if isinstance(msg, DeviceRemoved) and not handled:
            newDevice: iDevice = msg.device
            verbose(f"Device removed id={newDevice.id}")
            self.removeDevice(newDevice)
            self.raiseEvent("DEVICE_REMOVED", newDevice)
            handled = True

        await Client.processMessage(self, message=msg, handled=handled)
