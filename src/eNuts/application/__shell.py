# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import List

# ==================================================================================
from PySide6.QtWidgets import QLayout

# ==================================================================================
from jAGQt.types.interface.window import iMainWindowBase

# ==================================================================================
from ..types.interface.application import ieNutsService, iShell


# ==================================================================================
class TrainingShell(iShell):
    def intializeUI(self: iMainWindowBase): 
        layout: QLayout | None = self.Layout


    def initializeInstance(self: iMainWindowBase): ...
    def bindServices(self, services: List[ieNutsService]): ... 
    