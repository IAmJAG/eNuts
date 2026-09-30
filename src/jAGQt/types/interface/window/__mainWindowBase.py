# ==================================================================================
# src/jAGQt/types/interface/window/__mainWindowBase.py
# ==================================================================================
from PySide6.QtCore import QSettings

# ==================================================================================


# ==================================================================================
class iMainWindowBase:
    def __init__(self, name: str = None, frameless: bool = False, *args, **kwargs) -> None: ...
    def saveWindowState(self) -> None: ...
    def restoreWindowsState(self) -> None: ...
    @property
    def Settings(self) -> QSettings: ...
