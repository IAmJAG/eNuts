# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Any, Optional

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QBoxLayout,
    QComboBox,
    QLabel,
    QListWidget,
    QSizePolicy,
    QWidget,
)

# ==================================================================================
from jAGQt.utilities import newLayout
from jAGQt.widgets.page import Page

# ==================================================================================
from ..navigation import PAGE_KG_RECORDER
from ..widgets import CaptureImage


# ==================================================================================
def buildKGRecorderPage(key: str = PAGE_KG_RECORDER) -> Page:
    """Key & Gesture Recorder page (pure view).

    Layout:
      left  - CaptureImage (stream + event source)
      right - configuration strip (device combo first), status, event list
      bottom CommandBar - Start/Stop | Clear | Save/Open

    Recording logic lives in KGRecorder (ENUTSWindow component).
    """
    page = Page(
        title="Key & Gesture Recorder",
        description="Capture keys and gestures",
        commandBarOn=True,
        id=key,
    )

    # --- content root: horizontal split ---
    contentRoot = QWidget()
    contentRoot.setObjectName("W_KG_RECORDER_CONTENT")
    contentRoot.setSizePolicy(
        QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
    )
    rootLayout: QBoxLayout = newLayout(
        QBoxLayout,
        spacing=8,
        margins=(8, 8, 8, 8),
        direction=QBoxLayout.Direction.LeftToRight,
    )
    contentRoot.setLayout(rootLayout)

    # Left: capture Image
    capture = CaptureImage(bg="#1a1a1a", backend="software")
    capture.setObjectName("W_KG_RECORDER_CAPTURE")
    capture.setSizePolicy(
        QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
    )
    capture.setMinimumSize(320, 240)
    rootLayout.addWidget(capture, 3)

    # Right: config strip + status + event list
    right = QWidget()
    right.setObjectName("W_KG_RECORDER_RIGHT")
    right.setSizePolicy(
        QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding
    )
    right.setMinimumWidth(260)
    rightLayout: QBoxLayout = newLayout(
        QBoxLayout,
        spacing=8,
        margins=(0, 0, 0, 0),
        direction=QBoxLayout.Direction.TopToBottom,
    )
    right.setLayout(rightLayout)

    # Configuration strip (expandable)
    configStrip = QWidget()
    configStrip.setObjectName("W_KG_RECORDER_CONFIG")
    configLayout: QBoxLayout = newLayout(
        QBoxLayout,
        spacing=4,
        margins=(0, 0, 0, 0),
        direction=QBoxLayout.Direction.TopToBottom,
    )
    configStrip.setLayout(configLayout)

    deviceLabel = QLabel("Device")
    deviceLabel.setObjectName("W_KG_RECORDER_DEVICE_LABEL")
    deviceCombo = QComboBox()
    deviceCombo.setObjectName("W_KG_RECORDER_DEVICE_COMBO")
    deviceCombo.setSizePolicy(
        QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
    )
    deviceCombo.addItem("(no devices)", None)
    configLayout.addWidget(deviceLabel)
    configLayout.addWidget(deviceCombo)
    rightLayout.addWidget(configStrip, 0)

    statusLabel = QLabel("Idle")
    statusLabel.setObjectName("W_KG_RECORDER_STATUS")
    statusLabel.setAlignment(
        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
    )
    rightLayout.addWidget(statusLabel, 0)

    eventList = QListWidget()
    eventList.setObjectName("W_KG_RECORDER_EVENT_LIST")
    eventList.setSizePolicy(
        QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
    )
    rightLayout.addWidget(eventList, 1)

    rootLayout.addWidget(right, 1)
    page.addWidget(contentRoot, stretch=1)

    # CommandBar groups: Recording | Session | Persistence
    page.addCommandGroup("Recording")
    page.addCommand("Start", group="Recording")
    page.addCommand("Stop", group="Recording")
    page.addCommandStretch(1)
    page.addCommandGroup("Session")
    page.addCommand("Clear", group="Session")
    page.addCommandGroup("Persistence")
    page.addCommand("Save", group="Persistence")
    page.addCommand("Open", group="Persistence")

    # Stash for controller / WorkSpace binding
    page._captureImage = capture  # type: ignore[attr-defined]
    page._deviceCombo = deviceCombo  # type: ignore[attr-defined]
    page._statusLabel = statusLabel  # type: ignore[attr-defined]
    page._eventList = eventList  # type: ignore[attr-defined]
    page._configStrip = configStrip  # type: ignore[attr-defined]

    verbose(f"[pages] kg-recorder page key={key!r}")
    return page
