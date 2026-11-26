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
        verbose(
            f"DeviceManager received message={type(msg).__name__} "
            f"handled={handled} trackedDevices={len(self._devices)}"
        )
        if handled:
            return

        if isinstance(msg, DeviceListInitialized) and not handled:
            newDevices: List[iDevice] = list(msg.payload.values())
            verbose(
                "Processing DeviceListInitialized "
                f"count={len(newDevices)} ids={sorted(device.id for device in newDevices)}"
            )
            for device in newDevices:
                self.addDevice(device)
            verbose(f"Raising DEVICE_LIST_INITIALIZED count={len(newDevices)}")
            self.raiseEvent("DEVICE_LIST_INITIALIZED", newDevices)
            handled = True

        if isinstance(msg, DeviceAdded) and not handled:
            newDevice: iDevice = msg.device
            verbose(f"Processing DeviceAdded id={newDevice.id}")
            self.addDevice(newDevice)
            verbose(f"Raising DEVICE_ADDED id={newDevice.id}")
            self.raiseEvent("DEVICE_ADDED", newDevice)
            handled = True

        if isinstance(msg, DeviceRemoved) and not handled:
            newDevice: iDevice = msg.device
            verbose(f"Processing DeviceRemoved id={newDevice.id}")
            self.removeDevice(newDevice)
            verbose(f"Raising DEVICE_REMOVED id={newDevice.id}")
            self.raiseEvent("DEVICE_REMOVED", newDevice)
            handled = True

        # iDeviceManager is the first base class and declares a Protocol stub
        # named processMessage. super() would resolve to that stub instead of
        # Client.processMessage, preventing Heartbeat from refreshing the lease.
        await Client.processMessage(self, msg, handled=handled)
