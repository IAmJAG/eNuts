# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional, Union

# ==================================================================================
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
from jAGQt.widgets import GLImage
from jAGQt.widgets.page import Page

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

    def _wInitializeUI(self) -> None:
        # Page chrome only — do not call PlaybackBase (it would insert a first GLImage).
        Page._wInitializeUI(self)

        layout: QBoxLayout = self.Layout
        layout.setDirection(QBoxLayout.Direction.LeftToRight)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        image: GLImage = GLImage(bg="#1a1a1a")
        image.setObjectName(f"{self.OBJECT_NAME}_STREAM")
        image.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        image.setMinimumSize(320, 240)

        deviceLabel: QLabel = QLabel("Device:")
        deviceCombo: QComboBox = QComboBox(placeholderText="Select Device")
        deviceCombo.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )

        deviceLayout: QHBoxLayout = QHBoxLayout()
        deviceLayout.setContentsMargins(0, 5, 0, 0)
        deviceLayout.setSpacing(5)
        deviceLayout.addWidget(deviceLabel)
        deviceLayout.addWidget(deviceCombo, stretch=1)

        utilsLayout: QBoxLayout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        utilsLayout.setContentsMargins(0, 0, 0, 0)
        utilsLayout.setSpacing(4)
        utilsLayout.addLayout(deviceLayout)
        utilsLayout.addStretch(1)

        utils: QWidget = QWidget()
        utils.setObjectName(f"{self.OBJECT_NAME}_UTILS")
        utils.setFixedWidth(250)
        utils.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        utils.setLayout(utilsLayout)

        # Page.addWidget forces Expanding + stretch; keep min size after add.
        self.addWidget(image, stretch=1)
        image.setMinimumSize(320, 240)
        self.Layout.addWidget(utils, 0)

        self._streamView = image
        self._deviceCombo = deviceCombo

        verbose(
            f"[KGRecorder] page id={self.Id!r} stream={image.objectName()!r} "
            f"utilsWidth=250"
        )
