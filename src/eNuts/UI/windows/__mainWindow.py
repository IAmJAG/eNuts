# ==================================================================================
from functools import wraps
from typing import Callable

# ==================================================================================
from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtWidgets import QBoxLayout, QLabel, QLayout, QLayoutItem, QWidget

# ==================================================================================
from jAGFx.workflow import workflow
from jAGQt.widgets import SideBar
from jAGQt.widgets.components import ItemDisplayMode
from jAGQt.window import MainWindowBase

# ==================================================================================
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
class MainWindow(MainWindowBase, ApplicationInformation):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__("ENUTS_WINDOW", *args, **kwargs)

    # ==================================================================================
    def _wInitializeUI(self) -> None:
        # WindowBase creates the central widget and self._layout.
        # Workflow metadata is replaced (not merged) by subclasses, so we must
        # call the base implementation explicitly.
        super()._wInitializeUI()

        # Horizontal root layout: SideBar | Content
        self._layout.setDirection(QBoxLayout.Direction.LeftToRight)
        self.ContentSpacing = 0
        self.ContentMargins = 0

        # ----- SideBar -------------------------------------------------------
        self._sideBar = SideBar(
            title="eNuts",
            expandedWidth=220,
            collapsedWidth=52,
            iconSize=22,
            startCollapsed=False,
            autoCollapse=False,
            animationDurationMs=240,
            parent=self,
        )

        # Sample navigation items so we can see the sidebar immediately
        self._sideBar.AddItem(text="Dashboard", icon=None)
        self._sideBar.AddItem(text="Devices", icon=None)
        self._sideBar.AddItem(text="Training", icon=None)
        self._sideBar.AddStretch()
        self._sideBar.AddItem(text="Settings", icon=None)
        

        self._sideBar.ItemClicked.connect(self._onSideBarItemClicked)

        # ----- Central content placeholder -----------------------------------
        self._contentArea = QWidget(self)
        self._contentArea.setObjectName("MainContentArea")
        lContentLayout = QBoxLayout(QBoxLayout.Direction.TopToBottom, self._contentArea)
        lContentLayout.setContentsMargins(16, 16, 16, 16)

        lPlaceholder = QLabel("Main content area – SideBar is live", self._contentArea)
        lPlaceholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lPlaceholder.setStyleSheet("color: #888888; font-size: 14px;")
        lContentLayout.addWidget(lPlaceholder, 1)

        # Assemble
        self._layout.addWidget(self._sideBar)
        self._layout.addWidget(self._contentArea, 1)

    # ==================================================================================
    def _onSideBarItemClicked(self, item) -> None:
        # Temporary feedback – replace with real navigation later
        print(f"SideBar item clicked: {item.Text}")
