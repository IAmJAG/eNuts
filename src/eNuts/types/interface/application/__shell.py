# ==================================================================================
from __future__ import annotations

# ==================================================================================
from jAGQt.types.interface.window import iMainWindowBase

# ==================================================================================
from ..services.device import iDeviceManager
from .__applicationInformation import iApplicationInformation


# ==================================================================================
class iShell(iApplicationInformation):
    def _wInitializeUI(self: iMainWindowBase) -> None: ...

    @property
    def deviceManager(self) -> iDeviceManager: ...
