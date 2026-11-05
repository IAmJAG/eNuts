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
from fluxCore.stream import LocalDeviceStream
from fluxCore.types.interface.device import iDevice

# ==================================================================================
from ...application.device import (
    DEVICE_ADDED_EVENT,
    DEVICE_INITIALIZED_EVENT,
    DEVICE_REMOVED_EVENT,
)
from ...types.interface.application import iShell
from ...types.interface.application.device import iDeviceManager
from ..widgets import CaptureGLImage
from .__playbackBase import PlaybackBase

# ==================================================================================
C_SETTINGS_DEVICE_ID: str = "RECORDER_DEVICE_ID"
# ==================================================================================


# ==================================================================================
class KGRecorder(PlaybackBase):
    """KG Recorder page: device combo + stream view via LocalDeviceStream.

    Does not own emitter subscribe/decode/start/stop. All stream lifecycle goes
    through ``LocalDeviceStream.switchDevice``.
    """

    def __init__(
        self,
        title: str,
        description: str = "",
        icon: Optional[Union[QIcon, QPixmap, str]] = None,
        commandBarOn: bool = True,
        id: Optional[str] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(
            title=title,
            description=description,
            icon=icon,
            commandBarOn=commandBarOn,
            id=id,
            *args,
            **kwargs,
        )
        self._stream: LocalDeviceStream = LocalDeviceStream(ringSize=8)

    @classmethod
    def classname(cls) -> str:
        return cls.__name__

    def _refreshDeviceCombo(self, *args, **kwargs) -> None:
        try:
            deviceCombo: QComboBox = self._deviceCombo
            self.blockWidgetSignals(deviceCombo)

            deviceCombo.clear()
            devices: List[iDevice] = [d for d in list(self.deviceManager.values())]

            if len(devices) == 0 or not devices:
                deviceCombo.placeholderText = "<No Device Found>"
            else:
                deviceCombo.placeholderText = "<Select Device>"
                for device in devices:
                    name: str = device.name.strip().lower()
                    deviceCombo.addItem(name, device.id)

            deviceId = self.settings.value(C_SETTINGS_DEVICE_ID, EMPTY)
            idx = deviceCombo.findData(deviceId)
            if idx >= 0:
                deviceCombo.setCurrentIndex(idx)
            elif deviceCombo.count() > 0:
                deviceCombo.setCurrentIndex(0)
                deviceId = deviceCombo.itemData(0)

            self._setDevice(deviceId)

        except Exception as ex:
            warning(f"refresh device combo failed: {ex}")

        finally:
            self.restoreWidgetSignals(deviceCombo)

    def _setDevice(self, deviceId: Optional[str]) -> None:
        cleaned: Optional[str] = (str(deviceId).strip() if deviceId else "") or None
        self._persistDeviceId(cleaned)
        verbose(f"[{self.classname()}] setting deviceId={cleaned!r}")
        createTask(self._stream.switchDevice, self.deviceManager, cleaned)

    def _persistDeviceId(self, deviceId: Optional[str]) -> None:
        settings: QSettings = self.settings
        if settings is None:
            return
        try:
            value = (deviceId or "").strip()
            settings.setValue(C_SETTINGS_DEVICE_ID, value)
            verbose(f"persisted deviceId={value!r} key={C_SETTINGS_DEVICE_ID!r}")
        except Exception as ex:
            warning(f"persist deviceId failed: {ex}")

    def _wInitializeServices(self) -> None:
        super()._wInitializeServices()

    def _wBindComponents(self) -> None:
        super()._wBindComponents()
        cboDevices: QComboBox = self._deviceCombo
        cboDevices.currentTextChanged.connect(self._onDeviceChanged)

        deviceMngr: iDeviceManager = self.deviceManager
        deviceMngr.subscribe(DEVICE_INITIALIZED_EVENT, self._refreshDeviceCombo)
        deviceMngr.subscribe(DEVICE_ADDED_EVENT, self._onDeviceAdded)
        deviceMngr.subscribe(DEVICE_REMOVED_EVENT, self._onDeviceRemoved)

    def _onDeviceChanged(self, device: str, *args, **kwargs) -> None:
        cboDevices: QComboBox = self._deviceCombo
        deviceId = cboDevices.itemData(cboDevices.findText(device))
        self._setDevice(deviceId)

    def _onDeviceAdded(self, device: iDevice, *args, **kwargs) -> None:
        cboDevices: QComboBox = self._deviceCombo
        deviceId: str = device.id
        newIndex: int = cboDevices.findData(deviceId)
        if newIndex == -1:
            deviceName: str = device.name.strip().lower()
            cboDevices.addItem(deviceName, deviceId)
            verbose(f"added device={deviceId!r}:{deviceName!r}")

    def _onDeviceRemoved(self, device: iDevice, *args, **kwargs) -> None:
        cboDevices: QComboBox = self._deviceCombo
        deviceId: str = device.id
        index: int = cboDevices.findData(deviceId)
        if index != -1:
            cboDevices.removeItem(index)
            deviceName: str = device.name.strip().lower()
            verbose(f"removed device={deviceId!r}:{deviceName!r}")
            if self._stream._serial == deviceId:
                self._setDevice(None)

    def _wInitializeUI(self) -> None:
        super()._wInitializeUI(CaptureGLImage)

        view: CaptureGLImage = self._streamView
        self._stream.attachView(view)

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
            f"page id={self.Id!r} stream={view.objectName()!r} "
            f"utilsWidth=250"
        )

    @property
    def shell(self) -> iShell:
        return self.mainwindow

    @property
    def settings(self) -> QSettings:
        return self.shell.settings

    @property
    def deviceManager(self) -> iDeviceManager:
        return self.shell.deviceManager
