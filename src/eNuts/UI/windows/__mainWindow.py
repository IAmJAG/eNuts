# ==================================================================================
from asyncio import Event

# ==================================================================================
from jAGFx.workflow import workflow
from jAGQt.window import MainWindowBase

# ==================================================================================
from ...application import Shell
from ...configuration import ApplicationInformation


# ==================================================================================
@workflow(
    "Initialize",
    "InitalizeShellUI",
    "InitializeSettings",
    "InitializeInfo",
    "RestoreWindowsState",
)
class MainWindow(MainWindowBase, ApplicationInformation, Shell):
    def __init__(self, shutdownEvent: Event, *args, **kwargs) -> None:
        super().__init__("ENUTS_WINDOW", *args, **kwargs)
        self._shutdownEvent = shutdownEvent

    def closeEvent(self, event) -> None:
        self._shutdownEvent.set()
        super().closeEvent(event)
