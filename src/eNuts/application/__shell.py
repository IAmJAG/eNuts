# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import List

# ==================================================================================
from PySide6.QtWidgets import QBoxLayout

# ==================================================================================
from jAGQt.types.interface.window import iMainWindowBase

# ==================================================================================
from ..types.interface.application import iENUTSService, iShell


# ==================================================================================
class Shell(iShell):
    def _wIntializeUI(self: iMainWindowBase) -> None:
        try:
            layout: QBoxLayout = self.Layout
            layout.setDirection(QBoxLayout.Direction.LeftToRight)
            self.ContentSpacing = 0
            self.ContentMargins = 0

        except Exception as ex:
            error("[shell] intializeUI FAIL", ex)
    # ==================================================================================
    
    def initializeInstance(self: iMainWindowBase) -> None:
        pass

    def bindServices(self, services: List[iENUTSService]) -> None:
        pass
