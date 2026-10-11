# ==================================================================================
from asyncio import Event, to_thread
from typing import Dict, List

# ==================================================================================
from fluxCore.devices import SCRCPY
from fluxCore.types.interface.device import iDevice
from fluxCore.types.interface.devices import iSCRCPY
from fluxCore.types.interface.emitters import iSCRCPYEmitter
from jAGFx.services import AsyncSubscription
from jAGFx.workflow import workflow
from utilities import createTask

# ==================================================================================
from ..utilities.asyncADB import ADBDevices, SCRCPYDevices

# ==================================================================================
DEVICE_ADDED_EVENT = "deviceManager.deviceAdded"
DEVICE_REMOVED_EVENT = "deviceManager.deviceRemoved"
# ==================================================================================


# ==================================================================================
@workflow
class deviceManager(AsyncSubscription, Dict[str, iDevice]):    
    def __init__(self, shutdownEvent: Event, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._shutdownEvent = shutdownEvent

    async def _discovery(self) -> None:
        async def isShutingdown() -> bool: ...
        isShutingdown = self._shutdownEvent.is_set

        async def _getDevices() -> Dict[str, iDevice]:
            devices: Dict[str, iDevice] = dict[str, iDevice]()
            devices.update(await SCRCPYDevices())
            # upate devices with other type of devices
            #    devices.update(await _getOtherDevices())

            return devices
        
        while not isShutingdown():
            devices: Dict[str, iDevice] = await _getDevices()
            
            curDeviceIds: List[str] = list(devices.keys())
            oldDeviceIds: List[str] = list(self.keys())

            newDeviceIds: List[str] = list(set(curDeviceIds) - set(oldDeviceIds))
            removedDeviceIds: List[str] = list(set(oldDeviceIds) - set(curDeviceIds))
            
            for deviceId in newDeviceIds:
                device: iDevice = devices.get(deviceId, None)
                if devices is not None: self.addDevice(device)

            for deviceId in removedDeviceIds:
                self.removeDevice(deviceId)

    def _aRunDiscovery(self) -> None:
        async def _discoveryRunner() -> None:
            await self._discovery()

        createTask(_discoveryRunner)        

    def addDevice(self, device: iDevice) -> None:
        if device is None: return
        deviceId: str = str(device.id)
        self[deviceId] = device
        self.raiseEvent(DEVICE_ADDED_EVENT, device)
        return device

    def removeDevice(self, device: iDevice | str) -> iDevice:
        if device is None or device == "": return
        deviceId: str = device if isinstance(device, str) else str(device.id)
        device: iDevice = self.pop(deviceId, None)

        if device: 
            self.raiseEvent(DEVICE_REMOVED_EVENT, device)
            return device
        

        