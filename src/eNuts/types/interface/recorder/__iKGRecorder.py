# ==================================================================================
from __future__ import annotations

# ==================================================================================
from enum import Enum
from typing import Any, Optional, Protocol, runtime_checkable

# ==================================================================================
from PySide6.QtCore import QObject


# ==================================================================================
class eKGRecorderState(Enum):
    Idle = "idle"
    Recording = "recording"


# ==================================================================================
@runtime_checkable
class iKGRecorder(Protocol):
    """Contract for the Key & Gesture Recorder controller.

    Owned by ENUTSWindow; wired from Shell. Lives outside the Page.
    """

    @property
    def state(self) -> eKGRecorderState: ...

    @property
    def deviceId(self) -> Optional[str]: ...

    def setDeviceId(self, deviceId: Optional[str]) -> None: ...

    def start(self) -> None: ...

    def stop(self) -> None: ...

    def clear(self) -> None: ...

    def save(self, name: Optional[str] = None) -> None: ...

    def open(self, name: str) -> None: ...

    def bindPage(self, page: Any) -> None: ...

    def unbindPage(self) -> None: ...
