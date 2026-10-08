# ==================================================================================
from jAGFx.workflow import workflow
from jAGQt.window import MainWindowBase

# ==================================================================================
from ...application.__shell import Shell
from ...configuration import ApplicationInformation


# ==================================================================================
@workflow(
    "InitializeSettings", "InitializeUI", "InitializeShell",
    "RestoreWindowsState", "InitializeInfo",
)
class MainWindow(MainWindowBase, ApplicationInformation, Shell):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__("ENUTS_WINDOW", *args, **kwargs)

    def closeEvent(self, event) -> None:        
        if hasattr(self, "_emitter") and self._emitter is not None: 
            self._emitter.stop()            
        super().closeEvent(event)