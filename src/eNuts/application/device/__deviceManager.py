# ==================================================================================
from asyncio import Event
from asyncio import sleep as asyncSleep
from typing import Dict, Iterable, Iterator, List, Optional

# ==================================================================================
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
    """Discovers ADB/SCRCPY devices and raises add/remove/init events.

    Stores devices in an explicit dict (not ``dict`` subclass) so ``values()`` /
    ``keys()`` are always reliable for UI sync.
    """

    def __init__(self, shutdownEvent: Event, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._shutdownEvent = shutdownEvent
        self._devices: Dict[str, iDevice] = {}

    # ------------------------------------------------------------------ mapping API
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

    # ------------------------------------------------------------------ discovery
    async def _discovery(self) -> None:
        isShuttingDown = self._shutdownEvent.is_set

        async def _getDevices() -> Dict[str, iDevice]:
            found: Dict[str, iDevice] = {}
            found.update(await SCRCPYDevices())
            return found

        devices: Dict[str, iDevice] = await _getDevices()
        verbose(f"[deviceManager] initial discovery count={len(devices)} ids={list(devices.keys())}")

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
        verbose(
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

    def runDiscovery(self) -> None:
        async def _discoveryRunner() -> None:
            try:
                await self._discovery()
            except Exception as ex:
                error("[deviceManager] discovery FAIL", ex)

        createTask(_discoveryRunner)
        verbose("[deviceManager] runDiscovery scheduled")

    def addDevice(self, device: iDevice) -> Optional[iDevice]:
        if device is None:
            return None
        deviceId: str = str(device.id)
        self._devices[deviceId] = device
        verbose(f"[deviceManager] addDevice id={deviceId!r} name={getattr(device, 'name', None)!r}")
        self.raiseEvent(DEVICE_ADDED_EVENT, device)
        return device

    def removeDevice(self, device: iDevice | str) -> Optional[iDevice]:
        if device is None or device == "":
            return None
        deviceId: str = device if isinstance(device, str) else str(device.id)
        removed: Optional[iDevice] = self._devices.pop(deviceId, None)
        if removed is not None:
            verbose(f"[deviceManager] removeDevice id={deviceId!r}")
            self.raiseEvent(DEVICE_REMOVED_EVENT, removed)
            return removed
        return None
