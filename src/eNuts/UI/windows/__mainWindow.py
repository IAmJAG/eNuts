# ==================================================================================
from functools import wraps
from typing import Callable

# ==================================================================================
from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtWidgets import QBoxLayout, QLayout, QLayoutItem, QWidget

# ==================================================================================
from jAGFx.workflow import workflow
from jAGQt.window import MainWindowBase

# ==================================================================================
from ...application.__shell import Shell
from ...configuration import ApplicationInformation
from ..widgets import EvolvingNeuralBrain


# ==================================================================================
C_MORPH_METHODS: tuple[str, ...] = (
    "addWidget", "insertWidget", "addLayout", "insertLayout", "addItem",
    "insertItem", "addStretch", "addSpacing", "addStrut", "removeWidget",
    "removeItem", "takeAt",
)


# ==================================================================================
@workflow(
    "InitializeSettings", "InitializeUI", "RestoreWindowsState", "InitializeInfo"
)
class MainWindow(MainWindowBase, ApplicationInformation, Shell):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__("ENUTS_WINDOW", *args, **kwargs)

    # ==================================================================================
    def _wInitializeUI(self) -> None:
        # WindowBase creates the central widget and self._layout.
        super()._wInitializeUI()

        # Shell owns SideBar composition, content host, and navigation wiring.
        self.intializeUI()
