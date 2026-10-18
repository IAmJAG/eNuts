# ==================================================================================
from typing import Protocol, runtime_checkable

# ==================================================================================
from PySide6.QtCore import QSettings

# ==================================================================================
from jAGFx.types.interface.configuration import iApplicationConfiguration

# ==================================================================================
from ...components import iComponentBase

# iQMainWindow is a Protocol for typing/intellisense only. It must NOT appear in the
# runtime MRO of any QMainWindow subclass — its "..." method bodies would shadow
# real Qt virtuals (especially event()) and return None.


# ==================================================================================
class iWindowBase(iComponentBase):
    # Cooperative passthrough so MI still reaches QMainWindow / QObject.
    def __init__(self, frameless: bool = False, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def saveWindowState(self) -> None: ...
    def restoreWindowsState(self) -> None: ...

    @property
    def settings(self) -> QSettings: ...
    @property
    def config(self) -> iApplicationConfiguration: ...
