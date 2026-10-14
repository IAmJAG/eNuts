# ==================================================================================
import os

# ==================================================================================
from typing import Dict

# ==================================================================================
from PySide6.QtWidgets import QApplication

# ==================================================================================
from utilities.io import getConfigPath

# ==================================================================================
from .theme import loadStyles

# ==================================================================================
CONFIG_DIR: str = "themes"
# ==================================================================================

# ==================================================================================
class eNutsApplication(QApplication):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        themePath: str = getConfigPath(CONFIG_DIR)
        self._styles: Dict[str, str] = loadStyles(themePath)

    def setStyleSheet(self, name: str) -> None:
        
        super().setStyleSheet(self._styles[name.lower()])        