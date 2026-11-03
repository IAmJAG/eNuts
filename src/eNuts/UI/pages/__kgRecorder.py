# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import List, Optional, Union

# ==================================================================================
from PySide6.QtCore import QSettings
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QBoxLayout,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QWidget,
)

# ==================================================================================
from fluxCore.types.interface.device import iDevice

# ==================================================================================
from ...types.interface.application import iShell
from ...types.interface.application.device import iDeviceManager
from ..widgets import CaptureGLImage
from .__playbackBase import PlaybackBase

# ==================================================================================
DEVICE_ADDED_EVENT: str = "deviceManager.deviceAdded"
DEVICE_REMOVED_EVENT: str = "deviceManager.deviceRemoved"
DEVICE_INITIALIZED_EVENT: str = "deviceManager.deviceInitialized"

C_SETTINGS_DEVICE_ID: str = "RECORDER_DEVICE_ID"
# ==================================================================================

# ==================================================================================
class KGRecorder(PlaybackBase):
    def __init__(
        self, title: str, description: str = "",
        icon: Optional[Union[QIcon, QPixmap, str]] = None, commandBarOn: bool = True,
        id: Optional[str] = None, *args, **kwargs
    ) -> None:
        super().__init__(
            title=title, description=description, icon=icon,
            commandBarOn=commandBarOn, id=id, *args, **kwargs
        )

    def _refreshDeviceCombo(self, *args, **kwargs) -> None:
        deviceCombo: QComboBox = self._deviceCombo
        trace("REFRESH DEVICE COMBO")
        
        shell: iShell = self.mainwindow
        settings: QSettings = shell.settings

        deviceMngr: iDeviceManager = shell.deviceManager

        devices: List[iDevice] = [d for d in list(deviceMngr.values())]
        deviceId = settings.value(C_SETTINGS_DEVICE_ID, None)

        deviceCombo.blockSignals(True)
        deviceCombo.clear()
        if len(devices) == 0 or not devices:
            deviceCombo.placeholderText = "<No Device Found>"
        else:
            
            deviceCombo.placeholderText = "<Select Device>"
            for device in devices:
                deviceCombo.addItem(device.name, device.id)                

        deviceCombo.blockSignals(False)

    def _setDevice(self, deviceId: str) -> None:
        shell: iShell = self.mainwindow
        deviceMngr: iDeviceManager = shell.deviceManager
        self._persistDeviceId(deviceId)

    def _persistDeviceId(self, deviceId: Optional[str]) -> None:
        shell: iShell = self.mainwindow
        settings: QSettings = shell.settings

        if settings is None: return

        try:
            value = (deviceId or "").strip()
            settings.setValue(C_SETTINGS_DEVICE_ID, value)
            verbose(
                f"[{self.__class__.__name__}] persisted deviceId={value!r} key={C_SETTINGS_DEVICE_ID!r}"
            )

        except Exception as ex:
            warning(f"[{self.__class__.__name__}] persist deviceId failed: {ex}")

    def _wInitializeServices(self) -> None: 
        super()._wInitializeServices()        
        
    def _wBindComponents(self) -> None:
        super()._wBindComponents()
        deviceMngr: iDeviceManager = self.deviceManager
        deviceMngr.subscribe(DEVICE_INITIALIZED_EVENT, self._refreshDeviceCombo)
        deviceMngr.subscribe(DEVICE_ADDED_EVENT, self._onDeviceAdded)        
        deviceMngr.subscribe(DEVICE_REMOVED_EVENT, self._onDeviceRemoved)
        
    def _onDeviceAdded(self, device: str, *args, **kwargs) -> None:
        debug(f"added device={device!r}")

    def _onDeviceRemoved(self, device: str, *args, **kwargs) -> None:
        debug(f"remove device={device!r}")

    def _wInitializeUI(self) -> None:
        super()._wInitializeUI(CaptureGLImage)

        view: CaptureGLImage = self._streamView

        layout: QBoxLayout = self.Layout
        layout.setDirection(QBoxLayout.Direction.LeftToRight)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        deviceLabel: QLabel = QLabel("Device:")
        deviceCombo: QComboBox = QComboBox(placeholderText="Select Device")
        deviceCombo.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )

        deviceLayout: QHBoxLayout = QHBoxLayout()
        deviceLayout.setContentsMargins(0, 0, 0, 0)
        deviceLayout.setSpacing(5)
        deviceLayout.addWidget(deviceLabel)
        deviceLayout.addWidget(deviceCombo, stretch=1)

        utilsLayout: QBoxLayout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        utilsLayout.setContentsMargins(5, 5, 5, 5)
        utilsLayout.setSpacing(4)
        utilsLayout.addLayout(deviceLayout)
        utilsLayout.addStretch(1)

        utils: QWidget = QWidget()
        utils.setObjectName(f"{self.OBJECT_NAME}_UTILS")
        utils.setFixedWidth(250)
        utils.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        utils.setLayout(utilsLayout)

        self.Layout.addWidget(utils, 0)
        self._deviceCombo = deviceCombo

        verbose(
            f"[{self.__class__.__name__}] page id={self.Id!r} stream={view.objectName()!r} "
            f"utilsWidth=250"
        )

    @property
    def shell(self) -> iShell:
        return self.mainwindow

    @property
    def deviceManager(self) -> iDeviceManager:
        return self.shell.deviceManager