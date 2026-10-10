# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Dict, List

# ==================================================================================
from fluxCore.types.interface.device import iDevice

# ==================================================================================
from jAGQt.types.interface.window import iMainWindowBase

# ==================================================================================
from .__eNutsService import iENUTSService


# ==================================================================================
class iShell:
    def intializeUI(self: iMainWindowBase): ...
    def initializeInstance(self: iMainWindowBase): ...
    def bindServices(self, services: List[iENUTSService]): ...

    def AddDevice(self, device: iDevice) -> None: ...
    def RemoveDevice(self, device: iDevice) -> None: ...

    @property
    def Devices(self) -> Dict[str, iDevice]: ...
