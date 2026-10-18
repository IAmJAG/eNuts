# ==================================================================================
from asyncio import Event
from asyncio import sleep as asyncSleep
from typing import Dict, Iterable, Iterator, Optional

# ==================================================================================
from fluxCore.emitters.scrcpy import SCRCPYEmitter
from fluxCore.types.interface.device import iDevice
from jAGFx.services import AsyncSubscription

# ==================================================================================
from ...utilities.asyncADB import SCRCPYDevices

# ==================================================================================
DEVICE_ADDED_EVENT: str = "deviceManager.deviceAdded"
DEVICE_REMOVED_EVENT: str = "deviceManager.deviceRemoved"
DEVICE_INITIALIZED_EVENT: str = "deviceManager.deviceInitialized"
POLL_INTERVAL: float = 2.0
# ==================================================================================


# ==================================================================================
class deviceManager(AsyncSubscription):
    """App-wide device + SCRCPYEmitter registry."""

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

    def getEmitter(self, deviceId: str) -> Optional[SCRCPYEmitter]:
        device = self._devices.get(deviceId)
        if isinstance(device, SCRCPYEmitter):
            return device
        return None

    async def ensureRunning(self, deviceId: str) -> SCRCPYEmitter:
        emitter = self.getEmitter(deviceId)
        if emitter is None:
            raise KeyError(f"No SCRCPYEmitter registered for id={deviceId!r}")

        if not self._streamReady.get(deviceId, False):
            debug(f"[deviceManager] ensureRunning initialize id={deviceId!r}")
            await emitter.initialize()
            self._streamReady[deviceId] = True

        if not emitter.isRunning:
            debug(f"[deviceManager] ensureRunning start id={deviceId!r}")
            emitter.start()

        return emitter

    def _stopEmitter(self, device: iDevice) -> None:
        if not isinstance(device, SCRCPYEmitter):
            return
        deviceId = str(device.id)
        try:
            if device.isRunning:
                device.stop()
                debug(f"[deviceManager] stopped emitter id={deviceId!r}")
        except Exception as ex:
            warning(f"[deviceManager] stop emitter id={deviceId!r} failed: {ex}")
        self._streamReady.pop(deviceId, None)

    def stopAll(self) -> None:
        """Stop every running emitter (app shutdown)."""
        for device in list(self._devices.values()):
            self._stopEmitter(device)
        debug("[deviceManager] stopAll done")

    async def _discovery(self) -> None:
        isShuttingDown = self._shutdownEvent.is_set

        async def _getDevices() -> Dict[str, iDevice]:
            found: Dict[str, iDevice] = {}
            found.update(await SCRCPYDevices())
            return found

        devices: Dict[str, iDevice] = await _getDevices()
        debug(
            f"[deviceManager] initial discovery count={len(devices)} "
            f"ids={list(devices.keys())}"
        )

        self.setSuppressEvent(True)
        try:
            for deviceId, device in devices.items():
                if isShuttingDown():
                    break
                if device is not None:
                    self.addDevice(device)
        finally:
            self.setSuppressEvent(False)

        self.raiseEvent(DEVICE_INITIALIZED_EVENT, self)
        debug(
            f"[deviceManager] INITIALIZED stored={len(self._devices)} "
            f"ids={list(self._devices.keys())}"
        )

        while not isShuttingDown():
            devices = await _getDevices()

            curIds = set(devices.keys())
            oldIds = set(self._devices.keys())

            for deviceId in curIds - oldIds:
                device = devices.get(deviceId)
                if device is not None:
                    self.addDevice(device)

            for deviceId in oldIds - curIds:
                self.removeDevice(deviceId)

            if not isShuttingDown():
                await asyncSleep(POLL_INTERVAL)

        self.stopAll()

    def runDiscovery(self) -> None:
        async def _discoveryRunner() -> None:
            try:
                await self._discovery()
            except Exception as ex:
                error("[deviceManager] discovery FAIL", ex)

        createTask(_discoveryRunner)
        debug("[deviceManager] runDiscovery scheduled")

    def addDevice(self, device: iDevice) -> Optional[iDevice]:
        if device is None:
            return None
        deviceId: str = str(device.id)
        if deviceId in self._devices:
            return self._devices[deviceId]
        self._devices[deviceId] = device
        debug(
            f"[deviceManager] addDevice id={deviceId!r} "
            f"name={getattr(device, 'name', None)!r} "
            f"type={type(device).__name__}"
        )
        self.raiseEvent(DEVICE_ADDED_EVENT, device)
        return device

    def removeDevice(self, device: iDevice | str) -> Optional[iDevice]:
        if device is None or device == "":
            return None
        deviceId: str = device if isinstance(device, str) else str(device.id)
        removed: Optional[iDevice] = self._devices.pop(deviceId, None)
        if removed is not None:
            self._stopEmitter(removed)
            debug(f"[deviceManager] removeDevice id={deviceId!r}")
            self.raiseEvent(DEVICE_REMOVED_EVENT, removed)
            return removed
        return None
