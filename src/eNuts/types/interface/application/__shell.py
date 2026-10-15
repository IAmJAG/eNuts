# ==================================================================================
from __future__ import annotations

# ==================================================================================
from PySide6.QtWidgets import QMainWindow

# ==================================================================================
from jAGQt.types.interface.window import iMainWindowBase

# ==================================================================================
from .__applicationInformation import iApplicationInformation


# ==================================================================================
class iShell(iApplicationInformation):
    def _wInitializeUI(self: iMainWindowBase | QMainWindow) -> None: ...
    