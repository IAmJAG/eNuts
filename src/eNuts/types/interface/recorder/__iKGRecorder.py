# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Any, Optional, Protocol, runtime_checkable


# ==================================================================================
@runtime_checkable
class iKGRecorder(Protocol):
    """Contract for the Key & Gesture Recorder controller.

    Owned by ENUTSWindow; wired from Shell. Lives outside the Page.
    Scope: device selection, stream attach, page bind — not recording session.
    """

    @property
    def deviceId(self) -> Optional[str]: ...

    def setDeviceId(self, deviceId: Optional[str]) -> None: ...

    def setDeviceManager(self, mgr: Any) -> None: ...

    def bindPage(self, page: Any) -> None: ...

    def unbindPage(self) -> None: ...
