# ==================================================================================
from jAGFx.workflow import workflow
from jAGQt.window import MainWindowBase

# ==================================================================================
from ...configuration import ApplicationInformation


# ==================================================================================
@workflow(
    "InitializeSettings", "InitializeUI", "RestoreWindowsState",
    "InitializeInfo"
)
class MainWindow(MainWindowBase, ApplicationInformation):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__("ENUTS_WINDOW", frameless=False, *args, **kwargs)
