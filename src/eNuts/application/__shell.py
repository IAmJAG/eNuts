# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Any, Dict, List

# ==================================================================================
from adbutils import AdbDevice, adb
from PySide6.QtWidgets import QBoxLayout, QWidget

# ==================================================================================
from fluxCore.emitters.scrcpy import SCRCPYEmitter
from jAGQt.types import DockPosition
from jAGQt.types.interface.widgets.commandBar import iCommandBar, iCommandBarButton
from jAGQt.types.interface.window import iMainWindowBase
from jAGQt.widgets.commandBar import CommandBar
from jAGQt.widgets.sideBar import SideBar

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

            lCenter: QWidget = QWidget()
            lCenterLayout: QBoxLayout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
            lCenterLayout.setContentsMargins(0, 0, 0, 0)
            lCenterLayout.setSpacing(0)
            lCenter.setLayout(lCenterLayout)

            self._imageStreamer: imageStreamer = imageStreamer()

            commandBar: iCommandBar = CommandBar()
            cmdBtn: iCommandBarButton = commandBar.addButton("File")
            commandBar.addStretch()

            lCenterLayout.addWidget(self._imageStreamer)
            lCenterLayout.addWidget(commandBar)

            layout.addWidget(lCenter, 1)

            self._wInitializeSideBar()

        except Exception as ex:
            error(f"[{self.__class__.__name__}] InitializeUI FAIL", ex)

    def _wInitializeSideBar(self: iMainWindowBase) -> None:
        try:
            self._sideBar: SideBar = SideBar(title="eNuts")
            self._sideBar.DockSideChanged.connect(self._onSideBarDockChanged)
            self._sideBar.CollapsedChanged.connect(self._onSideBarCollapsedChanged)

            self._sideBar.AddItem(text="Home")

            lDevices = self._sideBar.AddGroup(title="Devices")
            lDevices.AddItem(text="Emulator")
            lDevices.AddItem(text="USB Device")
            lRemote = lDevices.AddGroup(title="Remote", startCollapsed=True)
            lRemote.AddItem(text="SSH Bridge")
            lRemote.AddItem(text="Cloud Node")

            lTools = self._sideBar.AddGroup(title="Tools", startCollapsed=True)
            lTools.AddItem(text="Recorder")
            lTools.AddItem(text="Settings")
            lDebug = lTools.AddGroup(title="Debug")
            lDebug.AddItem(text="Logs")
            lDebug.AddItem(text="Inspector")

            self._sideBar.AddStretch()

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
            if not hasattr(self, "Settings"):
                return
            lSettings = self.Settings
            lCollapsed = _asBool(lSettings.value(_C_SIDEBAR_COLLAPSED, False), default=False)
            lDockRaw = lSettings.value(_C_SIDEBAR_DOCK, "left")
            lDock = str(lDockRaw).strip().lower() if lDockRaw is not None else "left"
            if lDock not in ("left", "right"):
                lDock = "left"
            self._sideBar.RestoreState(lCollapsed, lDock)
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
