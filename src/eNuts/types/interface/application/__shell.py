# ==================================================================================
from __future__ import annotations

# ==================================================================================
from jAGQt.types.interface.window import iMainWindowBase

# ==================================================================================
from .__applicationInformation import iApplicationInformation


# ==================================================================================
class iShell(iApplicationInformation):
    def _wInitializeUI(self: iMainWindowBase) -> None: ...
    