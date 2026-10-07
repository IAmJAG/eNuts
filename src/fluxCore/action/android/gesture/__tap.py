# ==================================================================================
# src/fluxCore/actions/androidAction/touch/__tap.py
# ==================================================================================
import math
import random

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
from .__touch import Touch


# ==================================================================================
class Tap(Action):
    def __init__(
        self,
        x: int | float, y: int | float,
        tId: int = DEFAULT_FINGER_ID,
        resolution: iPoint = Point(0, 0),
        rngRadius: int = 5,
        *args,
        **kwargs,
    ):
        super().__init__(None, eCommandType.INJECT_TOUCH_EVENT, *args, **kwargs)        
        self.name = f"{self.name}_TAP_ID_{tId}_{x}x{y}".upper()

        width = int(resolution.x)
        height = int(resolution.y)

        x0 = min(max(x, 0), width)
        y0 = min(max(y, 0), height)

        self._pkgPressed: bytes = pack(">BQIIHHHI", eKeyState.DOWN.value, tId, x0, y0, width, height, PRESSURE_MAX, PRIMARY_BUTTON)

        x1, y1 = self._randomPoint(rngRadius, x, y)
        x1 = min(max(x1, 0), width)
        y1 = min(max(y1, 0), height)

        self._pkgReleased: bytes = pack(">BQIIHHHI", eKeyState.UP.value, tId, x1, y1, width, height, PRESSURE_MIN, PRIMARY_BUTTON)

    def _randomPoint(self, radius, x, y):
        theta = random.uniform(0, 2 * math.pi)
        x = int(x + radius * math.cos(theta))
        y = int(y + radius * math.sin(theta))
        return x, y

    def execute(self, control: iControlSocket):
        try:
            Action.execute(self, control, self._pkgPressed)
            Action.execute(self, control, self._pkgReleased)

        except Exception as ex:
            raise ex
