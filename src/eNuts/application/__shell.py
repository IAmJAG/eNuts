# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import List

# ==================================================================================
from PySide6.QtWidgets import QBoxLayout, QMainWindow

# ==================================================================================
from jAGQt.types.interface.window import iMainWindowBase

# ==================================================================================
from ..types.interface.application import iShell
from .__applicationInformation import ApplicationInformation
from .workspace import WorkSpace


# ==================================================================================
class Shell(ApplicationInformation):
    def _wInitializeUI(self: iMainWindowBase) -> None:
        try:
            print("[shell] intializeUI", flush=True)
            super()._wInitializeUI()

        except Exception as ex:
            error("[shell] intializeUI FAIL", ex)
    # ==================================================================================