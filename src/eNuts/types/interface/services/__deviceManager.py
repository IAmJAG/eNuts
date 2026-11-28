# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Protocol, runtime_checkable

# ==================================================================================
from fluxCore.types.interface.device import iDevice

# ==================================================================================
from .__serviceManager import iServiceManager


# ==================================================================================
@runtime_checkable
class iDeviceManager(iServiceManager, Protocol):
    def addDevice(self, device: iDevice): ...
    def removeDevice(self, device: str | iDevice) -> iDevice: ...
    