# ==================================================================================
from __future__ import annotations

from asyncio import Event

# ==================================================================================
from typing import Dict

# ==================================================================================
from fluxCore.types.interface.device import iDevice
from jAGQt.types.interface.window import iMainWindowBase

# ==================================================================================
from ..types.interface.application import iENUTSService, iShell
from .__deviceManager import DEVICE_ADDED_EVENT, DEVICE_REMOVED_EVENT, deviceManager


# ==================================================================================
class Shell(iShell):
    def _aInitialize(self):
        shutdownEvent: Event = self._shutdownEvent
        dm: deviceManager = deviceManager(shutdownEvent)

        dm.subscribe(DEVICE_ADDED_EVENT, self.onNewDevice)
        dm.subscribe(DEVICE_REMOVED_EVENT, self.onDeviceRemoved)

        self._devices = dm

    def onNewDevice(self, device: iDevice):
        print(f"onNewDevice: {device.id}")

    def onDeviceRemoved(self, device: iDevice):
        print(f"onDeviceRemoved: {device.id}")