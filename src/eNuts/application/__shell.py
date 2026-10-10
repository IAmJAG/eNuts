# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Dict, List, Optional

# ==================================================================================
from fluxCore.types.interface.device import iDevice
from jAGQt.types.interface.window import iMainWindowBase

# ==================================================================================
from ..types.interface.application import iENUTSService, iShell


# ==================================================================================
class Shell(iShell):
    """Device registry only. UI chrome is re-introduced layer by layer outside this file.

    Layer 0: this stub is not mixed into MainWindow.
    Later layers will call into UI builders and post-show device bind explicitly.
    """

    def _ensureDeviceState(self) -> None:
        if not hasattr(self, "_devices"):
            self._devices: Dict[str, iDevice] = {}
        if not hasattr(self, "_selectedDeviceId"):
            self._selectedDeviceId: Optional[str] = None

    @property
    def Devices(self) -> Dict[str, iDevice]:
        self._ensureDeviceState()
        return dict(self._devices)

    def AddDevice(self, device: iDevice) -> None:
        self._ensureDeviceState()
        if device is None:
            return
        self._devices[str(device.id)] = device

    def RemoveDevice(self, device: iDevice) -> None:
        self._ensureDeviceState()
        if device is None:
            return
        lId = str(device.id)
        if self._selectedDeviceId == lId:
            self._selectedDeviceId = None
        self._devices.pop(lId, None)

    async def initializeInstance(self: iMainWindowBase) -> None:
        """Layer 0: no-op. Devices/bind return in a later layer."""
        return

    def bindServices(self, services: List[iENUTSService]) -> None:
        pass
