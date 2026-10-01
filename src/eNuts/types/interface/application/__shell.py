# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import List

# ==================================================================================
from jAGQt.types.interface.window import iMainWindowBase

# ==================================================================================
from .__enutsService import ieNutsService


# ==================================================================================
class iShell:
    def intializeUI(self: iMainWindowBase): ...
    def initializeInstance(self: iMainWindowBase): ...
    def bindServices(self, services: List[ieNutsService]): ... 
    