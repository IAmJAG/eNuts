# ==================================================================================
from __future__ import annotations

# ==================================================================================
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import uuid4

# ==================================================================================
from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QIcon, QKeyEvent, QMouseEvent, QPixmap
from PySide6.QtWidgets import (
    QBoxLayout,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QWidget,
)

# ==================================================================================
from fluxCore.action.android.enums import eKeyCode, eKeyState
from fluxCore.action.android.gesture import Touch
from fluxCore.action.android.injectKey import InjectKeyPress, InjectKeyRelease
from fluxCore.geometry import Point
from fluxCore.stream import LocalDeviceStream
from fluxCore.types.interface.device import iDevice
from jAGQt.widgets.Canvas import GLCanvas
from jAGQt.widgets.commandBar import CommandBarButton

# ==================================================================================
from ...services.device import (
    DEVICE_ADDED_EVENT,
    DEVICE_INITIALIZED_EVENT,
    DEVICE_REMOVED_EVENT,
)
from ...services.recorder import KGRecorderService
from ...types.interface.application import iShell
from ...types.interface.services.device import iDeviceManager
from ...types.interface.services.recorder import iKGRecorderService
from .__helper import C_QT_TO_ANDROID
from .__playbackBase import PlaybackBase
from .__recorderState import eKGRecorderState

# ==================================================================================
C_SETTINGS_DEVICE_ID: str = "RECORDER_DEVICE_ID"
C_RECORDINGS_DIR: str = "recordings"
# ==================================================================================

# PLACEHOLDER_REMAINDER - need full file
