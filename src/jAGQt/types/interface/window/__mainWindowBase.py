# ==================================================================================
from PySide6.QtCore import QSettings

# ==================================================================================
from jAGFx.configuration import ApplicationConfiguration

# ==================================================================================
from .windowBase import iWindowBase


# ==================================================================================
class iMainWindowBase(iWindowBase):
    def __init__(self, name: str = None, frameless: bool = False, *args, **kwargs) -> None: ...
    def saveWindowState(self) -> None: ...
    def restoreWindowsState(self) -> None: ...
    @property
    def settings(self) -> QSettings: ...
    @property
    def config(self, ) -> ApplicationConfiguration: ...
