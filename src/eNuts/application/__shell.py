# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Any, Dict, List, Optional

# ==================================================================================
from adbutils import adb
from PySide6.QtWidgets import QBoxLayout, QLabel, QSizePolicy, QWidget

# ==================================================================================
from fluxCore.emitters.scrcpy import SCRCPYEmitter
from fluxCore.types.interface.device import iDevice
from jAGQt.types import DockPosition
from jAGQt.types.interface.window import iMainWindowBase
from jAGQt.widgets.dashboard import Card, DashboardGrid, dashboardConfig
from jAGQt.widgets.page import Page
from jAGQt.widgets.sideBar import SideBar, SideBarItem
from jAGQt.widgets.workspace import Workspace

# ==================================================================================
from ..types.interface.application import iENUTSService, iShell
from ..UI.widgets.streamer import imageStreamer
from .__streamBind import StreamPipeline

# ==================================================================================
_C_SIDEBAR_COLLAPSED = "sideBar/collapsed"
_C_SIDEBAR_DOCK = "sideBar/dockSide"

_C_PAGE_DASHBOARD = "page.dashboard"
_C_PAGE_RECORDER = "page.recorder"
_C_PAGE_SCREENSHOT = "page.screenshot"


# ==================================================================================
def _asBool(value: Any, default: bool = False) -> bool:
    """Parse QSettings values safely.

    QSettings often returns the strings \"true\"/\"false\". ``bool(\"false\")`` is
    True in Python, which incorrectly forced the SideBar to start collapsed.
    """
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    lText = str(value).strip().lower()
    if lText in ("1", "true", "yes", "on"):
        return True
    if lText in ("0", "false", "no", "off", ""):
        return False
    return default


# ==================================================================================
def _seedDashboard(grid: DashboardGrid) -> None:
    """Seed cards — spans are in 64px cell units; columns follow host width."""
    lStatus = Card(
        title="Status",
        minColSpan=2,
        minRowSpan=2,
        preferredColSpan=4,
        preferredRowSpan=2,
        variant="status",
    )
    lHint = QLabel("System overview")
    lHint.setObjectName("Card_BodyHint")
    lStatus.SetBodyWidget(lHint)

    lLive = Card(
        title="Live",
        minColSpan=2,
        minRowSpan=2,
        preferredColSpan=3,
        preferredRowSpan=4,
        variant="live",
    )
    lLive.SetBodyWidget(QLabel("Preview slot"))

    lStats = Card(
        title="Stats",
        minColSpan=2,
        minRowSpan=2,
        preferredColSpan=3,
        preferredRowSpan=2,
        variant="stat",
    )
    lStats.SetBodyWidget(QLabel("—"))

    lActions = Card(
        title="Quick Actions",
        minColSpan=2,
        minRowSpan=2,
        preferredColSpan=4,
        preferredRowSpan=2,
        variant="actions",
    )
    lActions.SetBodyWidget(QLabel("Start / Capture"))

    lLog = Card(
        title="Activity",
        minColSpan=4,
        minRowSpan=2,
        preferredColSpan=12,
        preferredRowSpan=2,
        variant="log",
    )
    lLog.SetBodyWidget(QLabel("Recent events"))

    grid.AddCard(lStatus, col=0, row=0, colSpan=4, rowSpan=2)
    grid.AddCard(lLive, col=4, row=0, colSpan=3, rowSpan=4)
    grid.AddCard(lStats, col=7, row=0, colSpan=3, rowSpan=2)
    grid.AddCard(lActions, col=0, row=2, colSpan=4, rowSpan=2)
    grid.AddCard(lLog, col=0, row=4, colSpan=12, rowSpan=2)


# ==================================================================================
class Shell(iShell):
    # ==================================================================================
    # UI — structural chrome only. Runs synchronously in the MainWindow workflow
    # (before show). No await in this section: every await after show is a paint
    # boundary under qasync.
    # ==================================================================================
    def _wInitializeShell(self: iMainWindowBase) -> None:
        try:
            layout: QBoxLayout = self.Layout
            layout.setDirection(QBoxLayout.Direction.LeftToRight)
            self.ContentSpacing = 0
            self.ContentMargins = 0

            self._buildCenterWorkspace()
            self._buildSideBar()

        except Exception as ex:
            error(f"[{self.__class__.__name__}] InitializeShell FAIL", ex)

    def _buildCenterWorkspace(self: iMainWindowBase) -> None:
        """Center column: workspace pages + live streamer host."""
        layout: QBoxLayout = self.Layout

        center: QWidget = QWidget()
        center.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        centerLayout: QBoxLayout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        centerLayout.setContentsMargins(0, 0, 0, 0)
        centerLayout.setSpacing(0)
        center.setLayout(centerLayout)

        self._imageStreamer: imageStreamer = imageStreamer()
        self._workspace: Workspace = Workspace()
        self._streamPipeline = StreamPipeline(self._imageStreamer)

        lDashboard: Page = Page("Dashboard", "Overview", id=_C_PAGE_DASHBOARD)
        lGrid: DashboardGrid = DashboardGrid(
            config=dashboardConfig(
                columns=12,
                minColumns=1,
                gap=8,
                cellSize=64,
                margins=8,
            )
        )
        _seedDashboard(lGrid)
        lDashboard.addWidget(lGrid)
        self._dashboardGrid = lGrid

        lRecorder: Page = Page(
            "Recorder",
            "Key & Gesture Recorder",
            commandBarOn=True,
            id=_C_PAGE_RECORDER,
        )
        lRecorder.addWidget(self._imageStreamer)
        lRecorder.addCommand("Start")
        lRecorder.addCommandStretch()

        lScreenshot: Page = Page(
            "Screenshot", "Capture device screen", id=_C_PAGE_SCREENSHOT
        )

        self._workspace.AddPage(lDashboard)
        self._workspace.AddPage(lRecorder)
        self._workspace.AddPage(lScreenshot)
        self._workspace.SetCurrentPage(_C_PAGE_RECORDER)

        centerLayout.addWidget(self._workspace, 1)
        layout.addWidget(center, 1)

    def _buildSideBar(self: iMainWindowBase) -> None:
        """SideBar + page links. Must complete before MainWindow.show()."""
        sideBar: SideBar = SideBar(title="eNuts")
        sideBar.DockSideChanged.connect(self._onSideBarDockChanged)
        sideBar.CollapsedChanged.connect(self._onSideBarCollapsedChanged)
        sideBar.ItemClicked.connect(self._onSideBarItemClicked)

        lDashItem = sideBar.AddItem(text="Dashboard", id=_C_PAGE_DASHBOARD)

        devices = sideBar.AddGroup(title="Devices")
        devices.AddItem(text="Emulator")

        dataCollector = sideBar.AddGroup(
            title="Data Collector", startCollapsed=True
        )
        lShotItem = dataCollector.AddItem(
            text="Screenshot", id=_C_PAGE_SCREENSHOT
        )
        lRecItem = dataCollector.AddItem(
            text="Recorder", id=_C_PAGE_RECORDER
        )

        training = sideBar.AddGroup(title="Training", startCollapsed=True)
        training.AddItem(text="<empty>")

        sideBar.AddGroup(title="Tools", startCollapsed=True)
        sideBar.AddStretch()

        self._sideBar = sideBar

        lDashboard = self._workspace.GetPage(_C_PAGE_DASHBOARD)
        lScreenshot = self._workspace.GetPage(_C_PAGE_SCREENSHOT)
        lRecorder = self._workspace.GetPage(_C_PAGE_RECORDER)
        if lDashboard is not None:
            self._workspace.Link(lDashItem, lDashboard)
        if lScreenshot is not None:
            self._workspace.Link(lShotItem, lScreenshot)
        if lRecorder is not None:
            self._workspace.Link(lRecItem, lRecorder)

        dataCollector.Expand(animate=False)
        sideBar.SelectItem(lRecItem)

        self._restoreSideBarState()

        lLayout: QBoxLayout = self.Layout
        lDock = self._sideBar.DockSide
        if lDock is DockPosition.Right:
            lLayout.addWidget(self._sideBar)
        else:
            lLayout.insertWidget(0, self._sideBar)

    def _onSideBarItemClicked(self, item: SideBarItem) -> None:
        try:
            if item is None:
                return
            self._workspace.NavigateByItem(item)
        except Exception as ex:
            error(f"[{self.__class__.__name__}] SideBar navigate FAIL", ex)

    def _restoreSideBarState(self: iMainWindowBase) -> None:
        try:
            if not hasattr(self, "Settings"):
                return

            settings = self.Settings
            collapsed = _asBool(
                settings.value(_C_SIDEBAR_COLLAPSED, False), default=False
            )
            dockRaw = settings.value(_C_SIDEBAR_DOCK, "left")
            dock = str(dockRaw).strip().lower() if dockRaw is not None else "left"
            if dock not in ("left", "right"):
                dock = "left"
            self._sideBar.RestoreState(collapsed, dock)

        except Exception as ex:
            error(f"[{self.__class__.__name__}] Restore SideBar state FAIL", ex)

    def _saveSideBarState(self: iMainWindowBase) -> None:
        try:
            if not hasattr(self, "Settings") or not hasattr(self, "_sideBar"):
                return
            lState = self._sideBar.ExportState()
            self.Settings.setValue(
                _C_SIDEBAR_COLLAPSED, 1 if lState["collapsed"] else 0
            )
            self.Settings.setValue(_C_SIDEBAR_DOCK, lState["dockSide"])
            self.Settings.sync()
        except Exception as ex:
            error(f"[{self.__class__.__name__}] Save SideBar state FAIL", ex)

    def _onSideBarDockChanged(self, position: DockPosition) -> None:
        try:
            lLayout: QBoxLayout = self.Layout
            lLayout.removeWidget(self._sideBar)
            if position is DockPosition.Left:
                lLayout.insertWidget(0, self._sideBar)
            else:
                lLayout.addWidget(self._sideBar)
            self._saveSideBarState()
        except Exception as ex:
            error(f"[{self.__class__.__name__}] SideBar dock change FAIL", ex)

    def _onSideBarCollapsedChanged(self, _collapsed: bool) -> None:
        self._saveSideBarState()

    # ==================================================================================
    # Non-UI — device registry, discovery, live stream bind.
    # Safe to await after show(); must not create or reparent shell chrome.
    # ==================================================================================
    def _ensureDeviceState(self) -> None:
        if not hasattr(self, "_devices"):
            self._devices: Dict[str, iDevice] = {}
        if not hasattr(self, "_selectedDeviceId"):
            self._selectedDeviceId: Optional[str] = None

    @property
    def Devices(self) -> Dict[str, iDevice]:
        self._ensureDeviceState()
        return dict(self._devices)

    def AddDevice(self, device: iDevice) -> None:
        self._ensureDeviceState()
        if device is None:
            return
        self._devices[str(device.id)] = device

    def RemoveDevice(self, device: iDevice) -> None:
        self._ensureDeviceState()
        if device is None:
            return
        lId = str(device.id)
        if self._selectedDeviceId == lId:
            self._unbindLivePipeline()
            self._selectedDeviceId = None
        self._devices.pop(lId, None)

    @property
    def SelectedDevice(self) -> Optional[iDevice]:
        self._ensureDeviceState()
        if self._selectedDeviceId is None:
            return None
        return self._devices.get(self._selectedDeviceId)

    def SelectDevice(self, deviceId: str | None) -> None:
        self._ensureDeviceState()
        if deviceId is None:
            self._unbindLivePipeline()
            self._selectedDeviceId = None
            return
        lId = str(deviceId)
        if lId not in self._devices:
            return
        self._selectedDeviceId = lId

    async def _discoverDevices(self) -> List[str]:
        """Return adb serials available now. Empty list if none."""
        try:
            lList = adb.device_list()
            return [str(d.serial) for d in lList if getattr(d, "serial", None)]
        except Exception as ex:
            error(f"[{self.__class__.__name__}] device discovery FAIL", ex)
            return []

    async def _startDeviceSession(self, serial: str) -> Optional[SCRCPYEmitter]:
        try:
            emitter: SCRCPYEmitter = SCRCPYEmitter(serial)
            await emitter.initialize()
            emitter.start()
            return emitter
        except Exception as ex:
            error(
                f"[{self.__class__.__name__}] start session FAIL serial={serial}",
                ex,
            )
            return None

    def _bindLivePipeline(self, device: iDevice) -> None:
        if not hasattr(self, "_streamPipeline") or self._streamPipeline is None:
            return
        if not hasattr(self, "_imageStreamer"):
            return
        self._streamPipeline.Bind(device)
        if hasattr(device, "subscribe"):
            device.subscribe("ON_FRAME", self._streamPipeline.OnFrame)

    def _unbindLivePipeline(self) -> None:
        if not hasattr(self, "_streamPipeline") or self._streamPipeline is None:
            return
        lDevice = self.SelectedDevice
        if lDevice is not None and hasattr(lDevice, "unsubscribe"):
            try:
                lDevice.unsubscribe("ON_FRAME", self._streamPipeline.OnFrame)
            except Exception:
                pass
        self._streamPipeline.Unbind()

    async def initializeInstance(self: iMainWindowBase) -> None:
        """Post-show non-UI bootstrap: discover → session → register → bind.

        Must not build or reparent shell chrome (SideBar, workspace, pages).
        Those run in _wInitializeShell before show().
        """
        try:
            lSerials = await self._discoverDevices()
            if not lSerials:
                warning(
                    f"[{self.__class__.__name__}] no adb devices; live stream idle"
                )
                return

            lPreferred = "emulator-5560"
            lSerial = lPreferred if lPreferred in lSerials else lSerials[0]

            emitter = await self._startDeviceSession(lSerial)
            if emitter is None:
                return

            self.AddDevice(emitter)
            self._emitter = emitter
            self.SelectDevice(str(emitter.id))
            self._bindLivePipeline(emitter)

        except Exception as ex:
            error(f"[{self.__class__.__name__}] InitializeInstance FAIL", ex)

    def bindServices(self, services: List[iENUTSService]) -> None:
        pass
