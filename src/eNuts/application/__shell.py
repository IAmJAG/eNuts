# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Dict, List

# ==================================================================================
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QBoxLayout, QStyle

# ==================================================================================
from jAGQt.types.interface.window import iMainWindowBase
from jAGQt.widgets import CommandBar, Page, SideBar, Workspace
from jAGQt.widgets.sideBar import SideBarItem

# ==================================================================================
from fluxCore.types.interface.device import iDevice

# ==================================================================================
from ..types.interface.application import iENUTSService, iShell
from ..UI.widgets.pages import KAndGRecorderPage


# ==================================================================================
class Shell(iShell):
    """Application shell: owns SideBar composition, Workspace content host, and device registry."""

    def intializeUI(self: iMainWindowBase) -> None:
        # Expect WindowBase._wInitializeUI to have already created self._layout
        self.Layout.setDirection(QBoxLayout.Direction.LeftToRight)
        self.ContentSpacing = 0
        self.ContentMargins = 0

        self._devices: Dict[str, iDevice] = {}

        self._sideBar = SideBar(
            title="eNuts", expandedWidth=220, collapsedWidth=52, iconSize=22,
            startCollapsed=False, autoCollapse=False, animationDurationMs=240,
            parent=self,
        )

        self._workspace: Workspace = Workspace(parent=self)
        self._workspace.setObjectName("MainWorkspace")

        self._buildSideBarNavigation()
        self._buildPages()
        self._sideBar.ItemClicked.connect(self._onSideBarItemClicked)

        self.Layout.addWidget(self._sideBar)
        self.Layout.addWidget(self._workspace, 1)

        self._navigateTo("Dashboard")

    # ==================================================================================
    def _standardIcon(self, standardPixmap: QStyle.StandardPixmap) -> QIcon:
        return self.style().standardIcon(standardPixmap)

    def _buildSideBarNavigation(self) -> None:
        """Primary nav + groups; Settings pinned to the bottom."""
        lBar: SideBar = self._sideBar

        lBar.AddItem(
            text="Dashboard",
            icon=self._standardIcon(QStyle.StandardPixmap.SP_DesktopIcon),
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
        lDevices.AddItem(
            text="K&G Recorder",
            icon=self._standardIcon(QStyle.StandardPixmap.SP_MediaPlay),
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

        lBar.AddStretch()
        lBar.AddSeparator()
        lBar.AddItem(
            text="Settings",
            icon=self._standardIcon(QStyle.StandardPixmap.SP_FileDialogInfoView),
        )

    def _buildPages(self) -> None:
        """Create a Page for every navigable sidebar entry."""
        lPages = [
            ("Dashboard", "Overview of the system"),
            ("DF Dashboard", "Data Factory overview"),
            ("Connected", "Connected devices and streams"),
            ("Sessions", "Active and past training sessions"),
            ("Models", "Trained and available models"),
            ("Settings", "Application configuration"),
        ]

        for lTitle, lDescription in lPages:
            lPage: Page = Page(title=lTitle, description=lDescription, parent=self._workspace)
            lBar = CommandBar(parent=lPage)
            lPage.CommandBar = lBar
            self._workspace.AddPage(lPage, name=lTitle)

        # Specialized recorder page (name must match sidebar text exactly)
        lRecorder = KAndGRecorderPage(parent=self._workspace)
        self._workspace.AddPage(lRecorder, name="K&G Recorder")

    # ==================================================================================
    def AddDevice(self, device: iDevice) -> None:
        """Register an iDevice in the global application collection."""
        if device is None:
            return
        self._devices[device.id] = device

    def RemoveDevice(self, device: iDevice) -> None:
        """Remove an iDevice from the global application collection."""
        if device is None:
            return
        self._devices.pop(device.id, None)

    @property
    def Devices(self) -> Dict[str, iDevice]:
        """Read-only view of registered devices keyed by iDevice.id."""
        return dict(self._devices)

    # ==================================================================================
    def _onSideBarItemClicked(self, item: SideBarItem) -> None:
        self._navigateTo(item.Text)

    def _navigateTo(self, pageName: str) -> None:
        self._workspace.SetCurrentPage(pageName)

    # ==================================================================================
    @property
    def Workspace(self) -> Workspace:
        return self._workspace

    @property
    def SideBar(self) -> SideBar:
        return self._sideBar

    def initializeInstance(self: iMainWindowBase) -> None:
        pass

    def bindServices(self, services: List[iENUTSService]) -> None:
        pass
