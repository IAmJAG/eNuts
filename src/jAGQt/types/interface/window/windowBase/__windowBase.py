# ==================================================================================
from typing import Protocol, runtime_checkable

# ==================================================================================
from PySide6.QtCore import QSettings

# ==================================================================================
from jAGFx.types.interface.configuration import iApplicationConfiguration

# ==================================================================================
from ...components import iComponentBase
from ...qt import iQMainWindow


# ==================================================================================
class iWindowBase(iQMainWindow, iComponentBase):
    def __init__(self, frameless: bool = False, *args, **kwargs) -> None: ...

    def saveWindowState(self) -> None: ...
    def restoreWindowsState(self) -> None: ...

    @property
    def settings(self) -> QSettings: ...
    @property
    def config(self) -> iApplicationConfiguration: ...
