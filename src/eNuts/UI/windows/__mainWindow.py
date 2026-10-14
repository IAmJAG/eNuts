# ==================================================================================
from asyncio import Event as asyncEvent

from jAGFx.workflow import workflow
from jAGQt.window import MainWindowBase

# ==================================================================================
from ...application.__shell import Shell
from ...configuration import ApplicationInformation


# ==================================================================================
@workflow("InitializeSettings", "InitializeUI", "RestoreWindowsState", "InitializeInfo")
class MainWindow(MainWindowBase, ApplicationInformation, Shell):
    def __init__(self, shutdownEvent: asyncEvent, *args, **kwargs) -> None:        
        super().__init__("ENUTS_WINDOW", *args, **kwargs)
        self._shutdownEvent: asyncEvent = shutdownEvent

    def closeEvent(self, event) -> None:
        self._shutdownEvent.set()
        super().closeEvent(event)