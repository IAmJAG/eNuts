# ==================================================================================
from asyncio import Event
from asyncio import sleep as asyncSleep
from typing import Dict, Iterable, Iterator, List, Optional, Union

# ==================================================================================
from fluxCore.emitters import SCRCPYEmitter
from fluxCore.types.interface.device import iDevice
from fluxCore.types.interface.emitters import iEmitter
from jAGFx.services import AsyncSubscription

# ==================================================================================
from ...types.interface.services.device import iDeviceManager
from ...utilities.asyncADB import SCRCPYDevices

# ==================================================================================
DEVICE_ADDED_EVENT: str = "deviceManager.deviceAdded"
DEVICE_REMOVED_EVENT: str = "deviceManager.deviceRemoved"
DEVICE_INITIALIZED_EVENT: str = "deviceManager.deviceInitialized"
POLL_INTERVAL: float = 2.0
# ==================================================================================


# ==================================================================================
class DeviceManager(iDeviceManager, AsyncSubscription):
    def __init__(self, shutdownEvent: Event, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._shutdownEvent = shutdownEvent
        self._devices: Dict[str, iDevice] = {}
        self._streamReady: Dict[str, bool] = {}

    def __len__(self) -> int:
        return len(self._devices)

    def __iter__(self) -> Iterator[str]:
        return iter(self._devices)

    def __contains__(self, key: object) -> bool:
        return key in self._devices

    def keys(self) -> Iterable[str]:
        return self._devices.keys()

    def values(self) -> Iterable[iDevice]:
        return self._devices.values()

    def items(self) -> Iterable[tuple[str, iDevice]]:
        return self._devices.items()

    def get(self, deviceId: str, default: Optional[iDevice] = None) -> Optional[iDevice]:
        return self._devices.get(deviceId, default)

    async def ensureRunning(self, deviceId: str) -> SCRCPYEmitter:
        emitter: SCRCPYEmitter = self.get(deviceId, None)
        if emitter is None:
            raise KeyError(f"No SCRCPYEmitter registered for id={deviceId!r}")

        if not self._streamReady.get(deviceId, False):
            verbose(f"ensureRunning initialize id={deviceId!r}")
            try:
                await emitter.initialize(GPUReady=False)

            except Exception as ex:
                self._streamReady[deviceId] = False
                error(f"ensureRunning initialize failed id={deviceId!r}", ex)
                raise

            self._streamReady[deviceId] = True

        if not emitter.isRunning:
            verbose(f"ensureRunning start id={deviceId!r}")
            emitter.start()

        return emitter

    def stop(self, device: Union[str, iDevice]) -> None:        
        if not isinstance(device, iEmitter): return        
        deviceId = str(device.id)
        try:
            if device.isRunning:
                device.stop()
                verbose(f"stopped emitter id={deviceId!r}")

        except Exception as ex:
            warning(f"stop emitter id={deviceId!r} failed", ex)

    def start(self, device: Union[str, iDevice]) -> None:
        if isinstance(device, str): device = self.get(device)
        if device is None or not isinstance(device, iEmitter): return
        deviceId = str(device.id)
        try:
            if not device.isRunning:
                device.start()
                verbose(f"started emitter id={deviceId!r}")
                
        except Exception as ex:
            warning(f"start emitter id={deviceId!r} failed", ex)

    def stopAll(self) -> None:
        for device in list(self._devices.values()):
            self.stop(device)

    def stopExcept(self, keepDeviceId: Union[str, iDevice]) -> None:
        keepId = keepDeviceId if isinstance(keepDeviceId, str) else str(keepDeviceId.id)
        for deviceId, device in list(self._devices.items()):
            if deviceId != keepId:
                self.stop(device)

    def add(self, device: iDevice) -> Optional[iDevice]:
        if device is None: return None
        deviceId = str(device.id)
        
        if deviceId in self._devices: return self._devices[deviceId]
        self._devices[deviceId] = device

        verbose(f"addDevice id={deviceId!r} type={type(device).__name__}")
        self.raiseEvent(DEVICE_ADDED_EVENT, device)
        return device

    def remove(self, device: iDevice | str) -> Optional[iDevice]:
        if device is None or device == "": return None
        
        deviceId: str = device if isinstance(device, str) else str(device.id)
        removed: Optional[iDevice] = self._devices.pop(deviceId, None)

        if removed is not None:
            self.stop(removed)
            verbose(f"removeDevice id={deviceId!r}")
            self.raiseEvent(DEVICE_REMOVED_EVENT, removed)
            return removed
        return None

    async def _discovery(self) -> None:
        isShuttingDown = self._shutdownEvent.is_set

        async def _getDevices() -> Dict[str, iDevice]:
            found: Dict[str, iDevice] = {}
            found.update(await SCRCPYDevices())
            return found

        devices: Dict[str, iDevice] = await _getDevices()
        verbose(f"initial discovery count={len(devices)} ids={list(devices.keys())}")

        try:
            self.setSuppressEvent(True)
            for deviceId, device in devices.items():
                if isShuttingDown(): return
                if device is not None: self.add(device)

        finally:
            self.setSuppressEvent(False)

        self.raiseEvent(DEVICE_INITIALIZED_EVENT, self)
        verbose(f"INITIALIZED stored={len(self._devices)} ids={list(self._devices.keys())}")

        while not isShuttingDown():
            devices: Dict[iDevice] = await _getDevices()            

            curIds = set(devices.keys())
            oldIds = set(self._devices.keys())

            for deviceId in curIds - oldIds:
                device = devices.get(deviceId)
                if device is not None: self.add(device)

            for deviceId in oldIds - curIds:
                self.remove(deviceId)

            if not isShuttingDown():
                await asyncSleep(POLL_INTERVAL)

        self.stopAll()

    def runDiscovery(self) -> None:
        async def _discoveryRunner() -> None:
            try:
                await self._discovery()

            except Exception as ex:
                error("discovery FAIL", ex)

        createTask(_discoveryRunner)
        verbose("runDiscovery scheduled")

    
