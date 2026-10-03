# ==================================================================================
from functools import wraps
from typing import Callable, Optional

# ==================================================================================
from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QBoxLayout,
    QLabel,
    QLayout,
    QLayoutItem,
    QStyle,
    QWidget,
)

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
        self._pageLabel: Optional[QLabel] = None

    # ==================================================================================
    def _standardIcon(self, standardPixmap: QStyle.StandardPixmap) -> QIcon:
        return self.style().standardIcon(standardPixmap)

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

        # Top-level
        self._sideBar.AddItem(
            text="Dashboard",
            icon=self._standardIcon(QStyle.StandardPixmap.SP_DesktopIcon),
        )

        # Devices group
        lDevices = self._sideBar.AddGroup(
            title="Devices",
            icon=self._standardIcon(QStyle.StandardPixmap.SP_ComputerIcon),
            startCollapsed=False,
        )
        lDevices.AddItem(
            text="Connected",
            icon=self._standardIcon(QStyle.StandardPixmap.SP_DriveHDIcon),
        )
        lDevices.AddItem(
            text="Available",
            icon=self._standardIcon(QStyle.StandardPixmap.SP_DriveNetIcon),
        )

        # Training group (starts collapsed)
        lTraining = self._sideBar.AddGroup(
            title="Training",
            icon=self._standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView),
            startCollapsed=True,
        )
        lTraining.AddItem(
            text="Sessions",
            icon=self._standardIcon(QStyle.StandardPixmap.SP_BrowserReload),
        )
        lTraining.AddItem(
            text="Models",
            icon=self._standardIcon(QStyle.StandardPixmap.SP_FileDialogListView),
        )

        self._sideBar.AddSeparator()
        self._sideBar.AddItem(
            text="Settings",
            icon=self._standardIcon(QStyle.StandardPixmap.SP_FileDialogInfoView),
        )
        self._sideBar.AddStretch()

        self._sideBar.ItemClicked.connect(self._onSideBarItemClicked)

        # ----- Central content -----------------------------------------------
        self._contentArea = QWidget(self)
        self._contentArea.setObjectName("MainContentArea")
        lContentLayout = QBoxLayout(QBoxLayout.Direction.TopToBottom, self._contentArea)
        lContentLayout.setContentsMargins(16, 16, 16, 16)

        self._pageLabel = QLabel("Dashboard", self._contentArea)
        self._pageLabel.setObjectName("PAGE_TITLE")
        self._pageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lContentLayout.addWidget(self._pageLabel, 1)

        # Assemble
        self._layout.addWidget(self._sideBar)
        self._layout.addWidget(self._contentArea, 1)

        self._navigateTo("Dashboard")

    # ==================================================================================
    def _onSideBarItemClicked(self, item) -> None:
        self._navigateTo(item.Text)

    def _navigateTo(self, pageName: str) -> None:
        if self._pageLabel is None:
            return
        self._pageLabel.setText(pageName)
