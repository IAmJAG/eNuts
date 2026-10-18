# ==================================================================================
from asyncio import to_thread
from typing import Dict, Optional

# ==================================================================================
from PySide6.QtWidgets import QApplication

# ==================================================================================
from utilities import createTask
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
        self._styles: Optional[Dict[str, str]] = None 
        self._pendingTheme: Optional[str] = None        

    async def asyncSetStyeSheet(self, themeName: str) -> None:
        themePath: str = getConfigPath(CONFIG_DIR)
        await self._loadStylesAsync(themePath)
        self.setStyleSheet(themeName)

    async def _loadStylesAsync(self, themePath: str) -> None:
        self._styles = None
        loadedStyles: Dict[str, str] = await to_thread(loadStyles, themePath)
        self._styles = loadedStyles

        if self._pendingTheme is not None:
            theme: str = self._pendingTheme
            self.setStyleSheet(theme)
            self._pendingTheme = None

    def setStyleSheet(self, themeName: str) -> None:
        key: str = themeName.strip().lower()
        if key in self._styles:
            styleSheet: str = self._styles.get(key, "")
            super().setStyleSheet(styleSheet)
            return

        warning(f"Theme '{key}' not found.")