# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import Event

from PySide6.QtWidgets import QMainWindow

# ==================================================================================
from fluxCore.types.interface.device import iDevice

# ==================================================================================
from ..types.interface.application import iENUTSService, iShell
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
        ws: Workspace = Workspace(self.Title)
        self.setCentralWidget(ws)        

    def _aInitialize(self):
        shutdownEvent: Event = self._shutdownEvent

        self._devices = deviceManager(shutdownEvent)

        self.bindDevices()        
        self._devices.runDiscovery()

    def bindDevices(self):
        initEvent: Event = self._getInitEvent()

        verbose("Binding devices")
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

    def onDeviceRemoved(self, device: iDevice):
        verbose(f"onDeviceRemoved: {device.id}")