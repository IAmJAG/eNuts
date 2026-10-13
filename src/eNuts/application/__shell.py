# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import Event
from typing import Dict, Optional

# ==================================================================================
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QBoxLayout, QMainWindow, QWidget

# ==================================================================================
from fluxCore.types.interface.device import iDevice
from jAGQt.utilities import newLayout
from jAGQt.widgets.sideBar import SideBarGroup, SideBarItem
from jAGQt.widgets.text import Text

# ==================================================================================
from ..types.interface.application import iShell
from ..UI.widgets.pages import C_PAGE_ID_DASHBOARD, DashboardPage
from .device import (
    DEVICE_ADDED_EVENT,
    DEVICE_INITIALIZED_EVENT,
    DEVICE_REMOVED_EVENT,
    deviceManager,
)
from .workspace import Workspace


# ==================================================================================
class Shell(iShell):
    def _getInitEvent(self) -> bool:
        if not hasattr(self, "_uiIntEvent"):
            self._uiIntEvent: Event = Event()

        return self._uiIntEvent

    def _wInitalizeShellUI(self: QMainWindow) -> None:
        self._devicesGroup: Optional[SideBarGroup] = None
        self._deviceMenuItems: Dict[str, SideBarItem] = {}

        # ws: Workspace = Workspace()        
        # QWidget.setStyleSheet(ws, "background-color: red; color: #f5f7fa;")        
        # self.setCentralWidget(ws)        
        # self._workspace: Workspace = ws
        # self._seedSideBar()

        testText: Text = Text("Hello World")

        layout: QBoxLayout = newLayout(QBoxLayout, spacing=0, margins=0, direction=QBoxLayout.Direction.TopToBottom)
        layout.addWidget(testText)

        ws: QWidget = QWidget()
        ws.setLayout(layout)

        self.setCentralWidget(ws)        

    def _seedSideBar(self) -> None:
        ws: Workspace = self._workspace
        sb = ws.SideBar

        dashPage = DashboardPage()
        ws.addPage(dashPage, name=C_PAGE_ID_DASHBOARD)

        dashItem = sb.AddItem(text="Dashboard", id=C_PAGE_ID_DASHBOARD)
        self._devicesGroup = sb.AddGroup(title="Devices")

        sb.selectItem(dashItem)
        ws.setCurrentPage(C_PAGE_ID_DASHBOARD)

    def _aInitialize(self):
        shutdownEvent: Event = self._shutdownEvent
        self._devices = deviceManager(shutdownEvent)

        self.bindDevices()
        self._devices.runDiscovery()

    def bindDevices(self):
        dm: deviceManager = self._devices
        dm.subscribe(DEVICE_ADDED_EVENT, self.onNewDevice)
        dm.subscribe(DEVICE_REMOVED_EVENT, self.onDeviceRemoved)
        dm.subscribe(DEVICE_INITIALIZED_EVENT, self.onDeviceInitialized)

    def onDeviceInitialized(self, deviceManager: deviceManager):
        for device in deviceManager.values():
            self.onNewDevice(device)
        verbose("DeviceManager initialized")

    def onNewDevice(self, device: iDevice):
        verbose(f"onNewDevice: {device.id}")
        # Discovery runs on the asyncio loop — marshal UI work to the Qt thread.
        QTimer.singleShot(0, lambda d=device: self._addDeviceMenuItem(d))

    def onDeviceRemoved(self, device: iDevice):
        verbose(f"onDeviceRemoved: {device.id}")
        QTimer.singleShot(0, lambda d=device: self._removeDeviceMenuItem(d))

    # ==================================================================================
    def _addDeviceMenuItem(self, device: iDevice) -> None:
        if device is None or self._devicesGroup is None:
            return

        deviceId: str = str(device.id)
        if deviceId in self._deviceMenuItems:
            return

        lLabel: str = device.name if device.name else deviceId
        lItem: SideBarItem = self._devicesGroup.AddItem(
            text=lLabel,
            id=deviceId,
        )
        self._deviceMenuItems[deviceId] = lItem

    def _removeDeviceMenuItem(self, device: iDevice) -> None:
        if device is None or self._devicesGroup is None:
            return

        deviceId: str = str(device.id)
        lItem = self._deviceMenuItems.pop(deviceId, None)
        if lItem is None:
            return
        self._devicesGroup.RemoveItem(lItem)

    # ==================================================================================
    def AddDevice(self, device: iDevice) -> None:
        if device is None:
            return
        self._devices.addDevice(device)

    def RemoveDevice(self, device: iDevice) -> None:
        if device is None:
            return
        self._devices.removeDevice(device)

    @property
    def Devices(self) -> Dict[str, iDevice]:
        return dict(self._devices)
