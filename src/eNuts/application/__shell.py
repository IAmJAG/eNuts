# ==================================================================================
from __future__ import annotations

# ==================================================================================
from time import sleep
from typing import Any, List

# ==================================================================================
from PySide6.QtWidgets import QBoxLayout, QWidget

# ==================================================================================
from fluxCore.emitters.scrcpy import SCRCPYEmitter
from jAGQt.types import DockPosition
from jAGQt.types.interface.widgets.commandBar import iCommandBar, iCommandBarButton
from jAGQt.types.interface.window import iMainWindowBase
from jAGQt.widgets.commandBar import CommandBar
from jAGQt.widgets.page import Page
from jAGQt.widgets.sideBar import SideBar, SideBarItem

# ==================================================================================
from ..types.interface.application import iENUTSService, iShell
from ..UI.widgets.streamer import imageStreamer

# ==================================================================================
_C_SIDEBAR_COLLAPSED = "sideBar/collapsed"
_C_SIDEBAR_DOCK = "sideBar/dockSide"


# ==================================================================================
def _asBool(value: Any, default: bool = False) -> bool:
    """Parse QSettings values safely.

    QSettings often returns the strings "true"/"false". ``bool("false")`` is
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
class Shell(iShell):
    def _wInitializeShell(self: iMainWindowBase) -> None:
        try:
            layout: QBoxLayout = self.Layout
            layout.setDirection(QBoxLayout.Direction.LeftToRight)
            self.ContentSpacing = 0
            self.ContentMargins = 0

            center: QWidget = QWidget()
            centerLayout: QBoxLayout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
            centerLayout.setContentsMargins(0, 0, 0, 0)
            centerLayout.setSpacing(0)
            center.setLayout(centerLayout)

            self._imageStreamer: imageStreamer = imageStreamer()

            recorder: Page = Page("Recorder", "Key & Gesture Recorder", commandBarOn=True)
            recorder.addWidget(self._imageStreamer)
            recorder.addCommand("Start", )            
            recorder.addCommandStretch()            
            centerLayout.addWidget(recorder)

            layout.addWidget(center, 1)            

        except Exception as ex:
            error(f"[{self.__class__.__name__}] InitializeUI FAIL", ex)

    def _initializeSideBar(self: iMainWindowBase) -> None:
        try:
            sideBar: SideBar = SideBar(title="eNuts")
            sideBar.DockSideChanged.connect(self._onSideBarDockChanged)
            sideBar.CollapsedChanged.connect(self._onSideBarCollapsedChanged)

            sideBar.AddItem(text="Dashboard")
            devices = sideBar.AddGroup(title="Devices")
            devices.AddItem(text="Emulator")

            dataCollector = sideBar.AddGroup(title="Data Collector", startCollapsed=True)
            dataCollector.AddItem(text="Screenshot")
            dataCollector.AddItem(text="Recorder")

            training = sideBar.AddGroup(title="Training", startCollapsed=True)
            training.AddItem(text="<empty>")

            lTools = sideBar.AddGroup(title="Tools", startCollapsed=True)
            
            sideBar.AddStretch()
            self._sideBar = sideBar            

            self._restoreSideBarState()

            lLayout: QBoxLayout = self.Layout
            lDock = self._sideBar.DockSide
            if lDock is DockPosition.Right:
                lLayout.addWidget(self._sideBar)
            else:
                lLayout.insertWidget(0, self._sideBar)

        except Exception as ex:
            error(f"[{self.__class__.__name__}] InitializeSideBar FAIL", ex)

    def _restoreSideBarState(self: iMainWindowBase) -> None:
        try:
            if not hasattr(self, "Settings"): return

            settings: SideBar = self.Settings

            collapsed = _asBool(settings.value(_C_SIDEBAR_COLLAPSED, False), default=False)
            dockRaw = settings.value(_C_SIDEBAR_DOCK, "left")
            dock = str(dockRaw).strip().lower() if dockRaw is not None else "left"

            sideBar = self._sideBar
            
            if dock not in ("left", "right"): dock = "left"
            sideBar.RestoreState(collapsed, dock)

        except Exception as ex:
            error(f"[{self.__class__.__name__}] Restore SideBar state FAIL", ex)

    def _saveSideBarState(self: iMainWindowBase) -> None:
        try:
            if not hasattr(self, "Settings") or not hasattr(self, "_sideBar"):
                return
            lState = self._sideBar.ExportState()
            # Store as int 0/1 so round-trip is unambiguous across platforms
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
    async def initializeInstance(self: iMainWindowBase) -> None:
        try:
            self._initializeSideBar()
            sleep(0.1)
            emitter: SCRCPYEmitter = SCRCPYEmitter("emulator-5560")
            await emitter.initialize()

            self._imageStreamer.Decoder = emitter.CodecContext
            self._imageStreamer.ControlSocket = emitter.ControlSocket
            self._imageStreamer.DeviceWidth = emitter.width
            self._imageStreamer.DeviceHeight = emitter.height

            emitter.subscribe("ON_FRAME", self._imageStreamer.OnFrame)
            emitter.start()

            self._emitter = emitter

        except Exception as ex:
            error(f"[{self.__class__.__name__}] InitializeInstance FAIL", ex)

    def bindServices(self, services: List[iENUTSService]) -> None:
        pass
