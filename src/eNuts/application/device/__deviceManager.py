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
from ...types.interface.application.device import iDeviceManager
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
            verbose(f"[{self.__class__.__name__}] ensureRunning initialize id={deviceId!r}")
            await emitter.initialize(GPUReady=False)
            self._streamReady[deviceId] = True

        if not emitter.isRunning:
            verbose(f"[{self.__class__.__name__}] ensureRunning start id={deviceId!r}")
            emitter.start()

        return emitter

    def stop(self, device: Union[str, iDevice]) -> None:        
        if not isinstance(device, iEmitter): return        
        deviceId = str(device.id)
        try:
            if device.isRunning:
                device.stop()
                verbose(f"[{self.__class__.__name__}] stopped emitter id={deviceId!r}")

        except Exception as ex:
            warning(
                f"[{self.__class__.__name__}] stop emitter id={deviceId!r} failed: {ex}"
            )

        self._streamReady.pop(deviceId, None)

    def stopAll(self) -> None:
        for device in list(self._devices.values()):
            if isinstance(device, iEmitter):                 
                if device.isRunning: 
                    verbose(f"[{self.__class__.__name__}] stopping id={device.id!r}")
                    device.stop()

        verbose(f"[{self.__class__.__name__}] stopAll done")

    def stopExcept(self, keepDeviceId: Optional[str]) -> None:
        keep = (keepDeviceId or "").strip() or None
        for device in list(self._devices.values()):
            if not isinstance(device, SCRCPYEmitter): continue
            if keep is not None and str(device.id) == keep: continue
            self.stop(device)
        verbose(f"[{self.__class__.__name__}] stopExcept keep={keep!r} done")

    def start(self, device: Union[str, iDevice]) -> None: 
        deviceId: str = str(device.id) if isinstance(device, iDevice) else device
        createTask(self.ensureRunning, deviceId)        

    def add(self, device: iDevice) -> Optional[iDevice]:
        if device is None: return None

        deviceId: str = str(device.id)

        if deviceId in self._devices: return self._devices[deviceId]
        self._devices[deviceId] = device

        verbose(
            f"[{self.__class__.__name__}] addDevice id={deviceId!r} "
            f"name={getattr(device, 'name', None)!r} "
            f"type={type(device).__name__}"
        )
        self.raiseEvent(DEVICE_ADDED_EVENT, device)
        return device

    def remove(self, device: iDevice | str) -> Optional[iDevice]:
        if device is None or device == "": return None
        deviceId: str = device if isinstance(device, str) else str(device.id)
        removed: Optional[iDevice] = self._devices.pop(deviceId, None)
        if removed is not None:
            self.stop(removed)
            verbose(f"[{self.__class__.__name__}] removeDevice id={deviceId!r}")
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
        verbose(
            f"[{self.__class__.__name__}] initial discovery count={len(devices)} "
            f"ids={list(devices.keys())}"
        )
        
        try:
            self.setSuppressEvent(True)
            for deviceId, device in devices.items():
                if isShuttingDown(): return
                if device is not None: self.add(device)

        finally:
            self.setSuppressEvent(False)

        self.raiseEvent(DEVICE_INITIALIZED_EVENT, self)
        verbose(
            f"[{self.__class__.__name__}] INITIALIZED stored={len(self._devices)} "
            f"ids={list(self._devices.keys())}"
        )

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
                error(f"[{self.__class__.__name__}] discovery FAIL", ex)

        createTask(_discoveryRunner)
        verbose(f"[{self.__class__.__class__}] runDiscovery scheduled")

    