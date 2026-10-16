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
    # Must call super() so cooperative MI still reaches QMainWindow / QObject.
    # A bare "..." body breaks the chain and triggers libshiboken errors.
    def __init__(self, frameless: bool = False, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def saveWindowState(self) -> None: ...
    def restoreWindowsState(self) -> None: ...

    @property
    def settings(self) -> QSettings: ...
    @property
    def config(self) -> iApplicationConfiguration: ...
