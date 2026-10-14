# ==================================================================================
# src/fluxCore/actions/androidAction/touch/__touch.py
# ==================================================================================
from struct import pack

from ....types.geometry import Point
from ....types.interface.geometry import iPoint

# ==================================================================================
from ....types.interface.sockets import iControlSocket
from ..__androidAction import AndroidAction as Action
from ..__const import (
    DEFAULT_FINGER_ID,
    PRESSURE_MAX,
    PRESSURE_MIN,
    PRIMARY_BUTTON,
)
from ..enums import (
    eCommandType,
    eKeyState,
)


class Touch(Action):
    def __init__(
        self,
        state: eKeyState,
        x: float | int,
        y: float | int,
        resolution: iPoint = Point(0, 0),
        tId: int = DEFAULT_FINGER_ID,
        *args,
        **kwargs,
    ):
        super().__init__(None, eCommandType.INJECT_TOUCH_EVENT, *args, **kwargs)
        self.name = f"{self.name}_{state.name}_ID_{tId}_{x}x{y}".upper()

        width = int(resolution.x)
        height = int(resolution.y)

        x = int(min(max(x, 0), width))
        y = int(min(max(y, 0), height))

        action = state.value
        pressure = PRESSURE_MIN if state.value == 1 else PRESSURE_MAX

        # Struct Layout matching scrcpy injection packet expectations:
        # >I : Action Code (4 bytes)
        # q  : Pointer ID / Touch ID (8 bytes)
        # I  : X coordinate (4 bytes)
        # I  : Y coordinate (4 bytes)
        # H  : Screen Width (2 bytes)
        # H  : Screen Height (2 bytes)
        # H  : Pressure (2 bytes)
        # I  : Action Buttons (4 bytes)
        # I  : ?
        self._pkg: bytes = pack(">BqiiHHHii", action, tId, x, y, width, height, pressure, PRIMARY_BUTTON, 1)

    def execute(self, control: iControlSocket):
        try:            
            super().execute(control, self._pkg)
        except Exception as ex:
            raise ex
