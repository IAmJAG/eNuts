# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Protocol, runtime_checkable

# ==================================================================================
from ..device import iDevice


# ==================================================================================
@runtime_checkable
class iDeviceInputAdapter(Protocol):
    """Platform-agnostic input → device actions.

    Accepts device-oriented coordinates and platform key codes (Android:
    eKeyCode / eMetaState via the concrete adapter). Host UI (Qt) mapping
    stays outside fluxCore.
    """

    def Attach(self, device: iDevice) -> None: ...

    def Detach(self) -> None: ...

    def TouchDown(self, x: int, y: int) -> None: ...

    def TouchMove(self, x: int, y: int) -> None: ...

    def TouchUp(self, x: int, y: int) -> None: ...

    def Scroll(self, x: int, y: int, hScroll: float, vScroll: float) -> None: ...

    def KeyDown(self, keyCode: object, metaState: object = None) -> None: ...

    def KeyUp(self, keyCode: object, metaState: object = None) -> None: ...
