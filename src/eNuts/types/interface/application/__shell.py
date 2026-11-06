# ==================================================================================
from __future__ import annotations

# ==================================================================================
from jAGQt.types.interface.window import iMainWindowBase

# ==================================================================================
from .__applicationInformation import iApplicationInformation
from ..services.device import iDeviceManager


# ==================================================================================
class iShell(iApplicationInformation):
    def _wInitializeUI(self: iMainWindowBase) -> None: ...

    @property
    def deviceManager(self) -> iDeviceManager: ...
