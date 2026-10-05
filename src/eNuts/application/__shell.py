# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import List, Optional

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QBoxLayout, QLabel, QStyle, QWidget

# ==================================================================================
from jAGQt.types.interface.window import iMainWindowBase
from jAGQt.widgets import SideBar
from jAGQt.widgets.sideBar import SideBarItem

# ==================================================================================
from ..types.interface.application import iENUTSService, iShell


# ==================================================================================
class Shell(iShell):
    """Application shell: owns SideBar composition and primary content host."""

    def intializeUI(self: iMainWindowBase) -> None:
        # Expect WindowBase._wInitializeUI to have already created self._layout
        self.Layout.setDirection(QBoxLayout.Direction.LeftToRight)
        self.ContentSpacing = 0
        self.ContentMargins = 0

        self._sideBar = SideBar(
            title="eNuts", expandedWidth=220, collapsedWidth=52, iconSize=22,
            startCollapsed=False, autoCollapse=False, animationDurationMs=240, parent=self,
        )

        self._buildSideBarNavigation()
        self._sideBar.ItemClicked.connect(self._onSideBarItemClicked)

        # ----- Central content host -----------------------------------------
        self._contentArea = QWidget(self)
        self._contentArea.setObjectName("MainContentArea")
        lContentLayout = QBoxLayout(QBoxLayout.Direction.TopToBottom, self._contentArea)
        lContentLayout.setContentsMargins(16, 16, 16, 16)
        
        self._pageLabel = QLabel("Dashboard", self._contentArea)
        self._pageLabel.setObjectName("PAGE_TITLE")
        self._pageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lContentLayout.addWidget(self._pageLabel, 1)

        self.Layout.addWidget(self._sideBar)
        self.Layout.addWidget(self._contentArea, 1)

        self._navigateTo("Dashboard")

    # ==================================================================================
    def _standardIcon(self, standardPixmap: QStyle.StandardPixmap) -> QIcon:
        return self.style().standardIcon(standardPixmap)

    def _buildSideBarNavigation(self) -> None:
        """Primary nav + groups; Settings pinned to the bottom."""
        lBar: SideBar = self._sideBar

        lBar.AddItem(
            text="Dashboard", icon=self._standardIcon(QStyle.StandardPixmap.SP_DesktopIcon),
        )

        lDevices = lBar.AddGroup(
            title="Data Factory(DF)",
            icon=self._standardIcon(QStyle.StandardPixmap.SP_ComputerIcon),
            startCollapsed=False,
        )
        lDevices.AddItem(
            text="DF Dashboard",
            icon=self._standardIcon(QStyle.StandardPixmap.SP_DriveHDIcon),
        )
        lDevices.AddItem(
            text="Connected",
            icon=self._standardIcon(QStyle.StandardPixmap.SP_DriveNetIcon),
        )

        lTraining = lBar.AddGroup(
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

        # Configuration / settings stay at the bottom of the sidebar
        lBar.AddStretch()
        lBar.AddSeparator()
        lBar.AddItem(text="Settings",
            icon=self._standardIcon(QStyle.StandardPixmap.SP_FileDialogInfoView),
        )

    # ==================================================================================
    def _onSideBarItemClicked(self, item: SideBarItem) -> None:
        self._navigateTo(item.Text)

    def _navigateTo(self, pageName: str) -> None:
        lLabel: Optional[QLabel] = getattr(self, "_pageLabel", None)
        if lLabel is None: return
        lLabel.setText(pageName)

    def initializeInstance(self: iMainWindowBase) -> None:
        pass

    def bindServices(self, services: List[iENUTSService]) -> None:
        pass
