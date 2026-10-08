# ==================================================================================
from struct import pack

# ==================================================================================
from ....types.geometry import Point
from ....types.interface.geometry import iPoint
from ....types.interface.sockets import iControlSocket
from ..__androidAction import AndroidAction as Action
from ..__const import PRIMARY_BUTTON
from ..enums import eCommandType


# ==================================================================================
class Scroll(Action):
    """Inject a scrcpy scroll event at device coordinates."""

    def __init__(
        self,
        x: float | int,
        y: float | int,
        hScroll: float = 0.0,
        vScroll: float = 0.0,
        resolution: iPoint = Point(0, 0),
        *args,
        **kwargs,
    ):
        lName = f"ANDROID_ACTION_INJECT_SCROLL_{int(x)}x{int(y)}"
        super().__init__(lName, eCommandType.INJECT_SCROLL_EVENT, *args, **kwargs)

        lWidth = int(resolution.x)
        lHeight = int(resolution.y)
        lX = int(min(max(x, 0), max(lWidth - 1, 0))) if lWidth > 0 else int(x)
        lY = int(min(max(y, 0), max(lHeight - 1, 0))) if lHeight > 0 else int(y)

        self._pkg: bytes = pack(
            ">IIHHffI",
            lX,
            lY,
            lWidth,
            lHeight,
            float(hScroll),
            float(vScroll),
            PRIMARY_BUTTON,
        )

    def execute(self, control: iControlSocket):
        try:
            super().execute(control, self._pkg)
        except Exception as ex:
            raise ex
