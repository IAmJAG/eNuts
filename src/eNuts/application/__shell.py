# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import List

# ==================================================================================
from PySide6.QtWidgets import QLayout

# ==================================================================================
from jAGQt.types.interface.window import iMainWindowBase

# ==================================================================================
from ..types.interface.application import iENUTSService, iShell


# ==================================================================================
class Shell(iShell):
    def intializeUI(self: iMainWindowBase): 
        pass

    def initializeInstance(self: iMainWindowBase): 
        pass
    def bindServices(self, services: List[iENUTSService]): 
        pass    
    