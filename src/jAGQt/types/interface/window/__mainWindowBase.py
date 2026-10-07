# ==================================================================================
# src/jAGQt/types/interface/window/__mainWindowBase.py
# ==================================================================================
from PySide6.QtCore import QSettings

# ==================================================================================
from .windowBase import iWindowBase


# ==================================================================================
class iMainWindowBase(iWindowBase):
    def __init__(self, name: str = None, frameless: bool = False, *args, **kwargs) -> None: ...
    def saveWindowState(self) -> None: ...
    def restoreWindowsState(self) -> None: ...
    @property
    def Settings(self) -> QSettings: ...
