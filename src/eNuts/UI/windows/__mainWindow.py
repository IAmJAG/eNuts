# ==================================================================================
from functools import wraps
from typing import Callable, Optional

# ==================================================================================
from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtWidgets import QBoxLayout, QLayout, QLayoutItem, QWidget

# ==================================================================================
from jAGFx.workflow import workflow
from jAGQt.widgets import SideBar
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
def _bindMorphMethods(target: object, layoutGetter: Callable[[], Optional[QLayout]]) -> None:
    """Expose layout mutation methods on *target* that forward to the live layout."""

    def _makeProxy(methodName: str) -> Callable:
        def _proxy(self, *args, **kwargs):
            lLayout = layoutGetter()
            if lLayout is None:
                raise RuntimeError(f"Cannot call {methodName}: content layout is not ready.")
            lMethod = getattr(lLayout, methodName)
            return lMethod(*args, **kwargs)

        _proxy.__name__ = methodName
        _proxy.__qualname__ = f"MainWindow.{methodName}"
        return _proxy

    for lName in C_MORPH_METHODS:
        if not hasattr(target, lName):
            setattr(target, lName, _makeProxy(lName).__get__(target, type(target)))


# ==================================================================================
@workflow(
    "InitializeSettings", "InitializeUI", "RestoreWindowsState", "InitializeInfo"
)
class MainWindow(MainWindowBase, ApplicationInformation, Shell):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__("ENUTS_WINDOW", *args, **kwargs)

    # ==================================================================================
    def _wInitializeUI(self) -> None:
        super()._wInitializeUI()

        # Shell owns SideBar composition, content host, and navigation wiring.
        self.intializeUI()

        # Morph methods operate on the central content area layout
        _bindMorphMethods(self, self._contentLayout)

    # ==================================================================================
    def _contentLayout(self) -> Optional[QLayout]:
        lArea = getattr(self, "_contentArea", None)
        if lArea is None:
            return None
        return lArea.layout()

    @property
    def SideBar(self) -> Optional[SideBar]:
        return getattr(self, "_sideBar", None)

    @property
    def ContentArea(self) -> Optional[QWidget]:
        return getattr(self, "_contentArea", None)
