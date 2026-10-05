# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtWidgets import QWidget

# ==================================================================================
from jAGFx.workflow import workflow
from jAGQt.widgets import SideBar, Workspace
from jAGQt.window import MainWindowBase

# ==================================================================================
from ...application.__shell import Shell
from ...configuration import ApplicationInformation
from ..widgets.spinners import EvolvingNeuralBrain


# ==================================================================================
@workflow("InitializeSettings", "InitializeUI", "RestoreWindowsState", "InitializeInfo")
class MainWindow(MainWindowBase, ApplicationInformation, Shell):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__("ENUTS_WINDOW", *args, **kwargs)

    # ==================================================================================
    def _wInitializeUI(self) -> None:
        super()._wInitializeUI()

        # Shell owns SideBar composition, Workspace content host, and navigation wiring.
        self.intializeUI()

    # ==================================================================================
    @property
    def SideBar(self) -> Optional[SideBar]:
        return getattr(self, "_sideBar", None)

    @property
    def Workspace(self) -> Optional[Workspace]:
        return getattr(self, "_workspace", None)

    @property
    def ContentArea(self) -> Optional[QWidget]:
        # retained for backward compatibility – now the Workspace itself
        return getattr(self, "_workspace", None)
