# ==================================================================================
# src/fluxCore/action/android/gesture/__touch.py
# ==================================================================================
from struct import pack

# ==================================================================================
from ....types.geometry import Point
from ....types.interface.geometry import iPoint
from ....types.interface.sockets import iControlSocket
from ..__androidAction import AndroidAction as Action
from ..__const import (
    DEFAULT_FINGER_ID,
    PRESSURE_MAX,
    PRESSURE_MIN,
    PRIMARY_BUTTON,
)
from ..enums import eCommandType, eKeyState


# ==================================================================================
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
        lName = f"ANDROID_ACTION_INJECT_TOUCH_{state.name}_ID_{tId}_{int(x)}x{int(y)}"
        super().__init__(lName, eCommandType.INJECT_TOUCH_EVENT, *args, **kwargs)

        width = int(resolution.x)
        height = int(resolution.y)

        x = int(min(max(x, 0), width)) if width > 0 else int(x)
        y = int(min(max(y, 0), height)) if height > 0 else int(y)

        action = state.value
        pressure = PRESSURE_MIN if state.value == eKeyState.UP.value else PRESSURE_MAX

        self._pkg: bytes = pack(
            ">BqiiHHHii",
            action,
            tId,
            x,
            y,
            width,
            height,
            pressure,
            PRIMARY_BUTTON,
            1,
        )

    def execute(self, control: iControlSocket):
        try:
            super().execute(control, self._pkg)
        except Exception as ex:
            raise ex
