# ==================================================================================
from __future__ import annotations

from asyncio import Task

# ==================================================================================
from typing import Dict, Optional, Union

# ==================================================================================
from adbutils import AdbDevice, adb

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QBoxLayout,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

# ==================================================================================
from fluxCore.emitters import SCRCPYEmitter
from fluxCore.types.interface.emitters import iSCRCPYEmitter
from jAGQt.widgets import GLImage

# ==================================================================================
from .__playbackBase import PlaybackBase


# ==================================================================================
class KGRecorder(PlaybackBase):
    """
    K&G Recorder page: GLImage stream + device strip + command bar chrome.
    Controller binds via Shell to:
        ``_streamView``, ``_deviceCombo``, ``_commandBar``, ``_statusLabel``, ``_eventList``.
    """
    def __init__(
        self, title: str, description: str = "",
        icon: Optional[Union[QIcon, QPixmap, str]] = None, commandBarOn: bool = True,
        id: Optional[str] = None, *args, **kwargs
    ) -> None:
        super().__init__(
            title=title, description=description, icon=icon, commandBarOn=commandBarOn,
            id=id, *args, **kwargs
        )

    def deviceChanged(self, device: str) -> None:
        self._deviceCombo.setCurrentText(device)

    def _initialize(self) -> None:
        # TODO: this will be a binding later
        adbDevices: Dict[str, AdbDevice] = {d.serial: d for d in adb.device_list()}
        devices: QComboBox = self._deviceCombo

        for d in adbDevices.values():
            emitter: iSCRCPYEmitter = SCRCPYEmitter(d.serial)
            task: Task = createTask(emitter.initialize)
            task.add_done_callback(lambda _: devices.addItem(d.name)) 

    def _wInitializeUI(self) -> None:
        super()._wInitializeUI()

        layout: QBoxLayout = self.Layout
        layout.setDirection(QBoxLayout.Direction.LeftToRight)

        image: GLImage = GLImage(bg="#1a1a1a")
        image.setObjectName(f"{self.OBJECT_NAME}_STREAM")
        image.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        image.setMinimumSize(320, 240)

        deviceLabel: QLabel = QLabel("Device:")
        deviceCombo: QComboBox = QComboBox(placeholderText="Select Device")
        
        deviceLayout: QHBoxLayout = QHBoxLayout()
        deviceLayout.setContentsMargins(0, 5, 0, 0)
        deviceLayout.setSpacing(5)

        deviceLayout.addWidget(deviceLabel)
        deviceLayout.addWidget(deviceCombo, stretch=1)

        utilsLayout: QBoxLayout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        utilsLayout.addLayout(deviceLayout)
        utilsLayout.addStretch(1)

        utils: QWidget = QWidget()
        utils.setFixedWidth(250)
        utils.setObjectName(f"{self.OBJECT_NAME}_UTILS")
        utils.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        utils.setLayout(utilsLayout)
        
        self.addWidget(image, stretch=1)
        self.addWidget(utils)

        self._streamView = image
        self._deviceCombo = deviceCombo

        self._initialize()