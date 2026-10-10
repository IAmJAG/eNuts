# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from ..action.android.enums import eKeyCode, eKeyState, eMetaState
from ..action.android.gesture import Scroll, Touch
from ..action.android.injectKey import InjectKeyPress, InjectKeyRelease
from ..types.geometry import Point
from ..types.interface.device import iDevice
from ..types.interface.deviceInput import iDeviceInputAdapter
from ..types.interface.sockets import iControlSocket


# ==================================================================================
class AndroidScrcpyInputAdapter(iDeviceInputAdapter):
    """Drive an Android/scrcpy control channel from device-space input."""

    def __init__(self) -> None:
        self._control: Optional[iControlSocket] = None
        self._width: int = 0
        self._height: int = 0
        self._device: Optional[iDevice] = None

    # ==================================================================================
    def Attach(self, device: iDevice) -> None:
        self._device = device
        self._control = getattr(device, "ControlSocket", None)
        self._width = int(getattr(device, "width", 0) or 0)
        self._height = int(getattr(device, "height", 0) or 0)

    def Detach(self) -> None:
        self._device = None
        self._control = None
        self._width = 0
        self._height = 0

    def _resolution(self) -> Point:
        return Point(self._width, self._height)

    def _ready(self) -> bool:
        return (
            self._control is not None
            and self._width > 0
            and self._height > 0
        )

    # ==================================================================================
    def TouchDown(self, x: int, y: int) -> None:
        self._injectTouch(eKeyState.DOWN, x, y)

    def TouchMove(self, x: int, y: int) -> None:
        self._injectTouch(eKeyState.MOVE, x, y)

    def TouchUp(self, x: int, y: int) -> None:
        self._injectTouch(eKeyState.UP, x, y)

    def Scroll(self, x: int, y: int, hScroll: float, vScroll: float) -> None:
        if not self._ready():
            return
        try:
            Scroll(
                x,
                y,
                hScroll=hScroll,
                vScroll=vScroll,
                resolution=self._resolution(),
            ).execute(self._control)
        except Exception as ex:
            error(f"[{self.__class__.__name__}] scroll inject failed", ex)

    def KeyDown(self, keyCode: object, metaState: object = None) -> None:
        if not isinstance(keyCode, eKeyCode):
            return
        lMeta = metaState if isinstance(metaState, eMetaState) else eMetaState.NONE
        if self._control is None:
            return
        try:
            InjectKeyPress(keyCode, metaState=lMeta).execute(self._control)
        except Exception as ex:
            error(f"[{self.__class__.__name__}] key down inject failed", ex)

    def KeyUp(self, keyCode: object, metaState: object = None) -> None:
        if not isinstance(keyCode, eKeyCode):
            return
        lMeta = metaState if isinstance(metaState, eMetaState) else eMetaState.NONE
        if self._control is None:
            return
        try:
            InjectKeyRelease(keyCode, metaState=lMeta).execute(self._control)
        except Exception as ex:
            error(f"[{self.__class__.__name__}] key up inject failed", ex)

    # ==================================================================================
    def _injectTouch(self, state: eKeyState, x: int, y: int) -> None:
        if not self._ready():
            return
        try:
            Touch(
                state,
                x,
                y,
                resolution=self._resolution(),
            ).execute(self._control)
        except Exception as ex:
            error(f"[{self.__class__.__name__}] touch inject failed", ex)
