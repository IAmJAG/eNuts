# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Dict, Optional, Union

# ==================================================================================
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QBoxLayout, QComboBox, QSizePolicy, QWidget

from fluxCore.device import SCRCPYDevice

# ==================================================================================
from fluxCore.types.interface.device import iDevice
from jAGQt.widgets import CanvasBase, GLCanvas

# ==================================================================================
from ...types.interface.application import iShell
from ...types.interface.services import iDeviceManager
from .__playbackBase import PlaybackBase


# ==================================================================================
class KGRecorder(PlaybackBase):
    def __init__(
        self, title: str, description: str,
        icon: QIcon | QPixmap | str | None = None,
        commandBarOn: bool = True, id: str | None = None, *args, **kwargs,
    ) -> None:
        super().__init__(
            title=title, description=description, icon=icon,
            commandBarOn=commandBarOn, id=id, *args, **kwargs,  # noqa: B026
        )

    async def _onDevicesListInitialized(self, devices: list[iDevice]):
        if len(devices) > 0:
            self._cboDevices.clear()
            device: SCRCPYDevice
            for device in devices:
                device.updateInfo()
                self._cboDevices.addItem(device.name, userData=device.id)

    async def _onDeviceAdded(self, device: iDevice):                
        self._cboDevices.addItem(device.name, userData=device.id)
    
    async def _onDeviceRemoved(self, device: iDevice):                
        index: int = self._cboDevices.findData(device.id)
        self._cboDevices.removeItem(index)

    def _bindDevices(self):
        main: iShell = self.mainwindow
        deviceManager: iDeviceManager = main.deviceManager
        deviceManager.subscribe("DEVICE_LIST_INITIALIZED", self._onDevicesListInitialized)
        deviceManager.subscribe("DEVICE_ADDED", self._onDeviceAdded)
        deviceManager.subscribe("DEVICE_REMOVED", self._onDeviceRemoved)

    def _wBindComponents(self):
        super()._wBindComponents()
        self._bindDevices()        

    def _wInitializeUI(self) -> None:
        super()._wInitializeUI()
        expandingPolicy: QSizePolicy.Policy = QSizePolicy.Policy.Expanding

        self.Layout.setDirection(QBoxLayout.Direction.LeftToRight)
        
        cboDevices: QComboBox = QComboBox(placeholderText="[select device]")

        sideLayout: QBoxLayout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        sideLayout.setContentsMargins(0, 0, 0, 0)        
        sideLayout.setSpacing(0)

        sideLayout.addWidget(cboDevices)
        sideLayout.addStretch()
        
        sideWidget: QWidget = QWidget()            
        sideWidget.setSizePolicy(QSizePolicy.Policy.Fixed, expandingPolicy)
        sideWidget.setFixedWidth(250)
        sideWidget.setLayout(sideLayout)
        
        self.addWidget(sideWidget)

        self._cboDevices: QComboBox = cboDevices
