# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional, Union

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QSizePolicy,
    QWidget,
)

# ==================================================================================
from .__playbackBase import PlaybackBase


# ==================================================================================
class KGRecorder(PlaybackBase):
    """K&G Recorder page: GLImage stream + device strip + command bar chrome.

    Controller binds via Shell to:
    ``_streamView``, ``_deviceCombo``, ``_commandBar``, ``_statusLabel``, ``_eventList``.
    """

    OBJECT_NAME = "W_KG_RECORDER"

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

    def _wInitializeUI(self) -> None:
        super()._wInitializeUI()

        strip = QWidget()
        strip.setObjectName(f"{self.OBJECT_NAME}_DEVICE_STRIP")
        strip.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        stripLayout = QHBoxLayout(strip)
        stripLayout.setContentsMargins(8, 4, 8, 4)
        stripLayout.setSpacing(8)

        deviceLabel = QLabel("Device")
        deviceLabel.setObjectName(f"{self.OBJECT_NAME}_DEVICE_LABEL")

        deviceCombo = QComboBox()
        deviceCombo.setObjectName(f"{self.OBJECT_NAME}_DEVICE_COMBO")
        deviceCombo.setMinimumWidth(220)
        deviceCombo.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        deviceCombo.addItem("(no devices)", None)

        statusLabel = QLabel("Idle")
        statusLabel.setObjectName(f"{self.OBJECT_NAME}_STATUS")
        statusLabel.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        statusLabel.setMinimumWidth(120)

        stripLayout.addWidget(deviceLabel)
        stripLayout.addWidget(deviceCombo, stretch=1)
        stripLayout.addWidget(statusLabel)

        contentLayout = self.Layout
        contentLayout.insertWidget(0, strip, stretch=0)

        eventList = QListWidget()
        eventList.setObjectName(f"{self.OBJECT_NAME}_EVENTS")
        eventList.setMinimumWidth(180)
        eventList.setMaximumWidth(280)
        eventList.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding
        )

        streamView = getattr(self, "_streamView", None)
        if streamView is not None:
            try:
                contentLayout.removeWidget(streamView)
            except Exception:
                pass

            row = QWidget()
            row.setObjectName(f"{self.OBJECT_NAME}_BODY")
            rowLayout = QHBoxLayout(row)
            rowLayout.setContentsMargins(0, 0, 0, 0)
            rowLayout.setSpacing(4)
            rowLayout.addWidget(streamView, stretch=1)
            rowLayout.addWidget(eventList, stretch=0)
            contentLayout.addWidget(row, stretch=1)

        if self._commandBar is not None:
            for caption in ("Start", "Stop", "Clear", "Save", "Open"):
                try:
                    self.addCommand(caption)
                except Exception as ex:
                    warning(f"[pages] KG command button {caption!r} failed: {ex}")

        self._deviceCombo = deviceCombo
        self._statusLabel = statusLabel
        self._eventList = eventList

        verbose(
            f"[pages] KGRecorder page id={self.Id!r} "
            f"stream={getattr(streamView, 'objectName', lambda: None)()!r} "
            f"combo={deviceCombo.objectName()!r} "
            f"commandBar={self._commandBar is not None}"
        )
