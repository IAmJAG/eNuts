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
        super().__init__(None, eCommandType.INJECT_SCROLL_EVENT, *args, **kwargs)
        self.name = f"{self.name}_{x}x{y}_H{hScroll}_V{vScroll}".upper()

        lWidth = int(resolution.x)
        lHeight = int(resolution.y)
        lX = int(min(max(x, 0), max(lWidth - 1, 0)))
        lY = int(min(max(y, 0), max(lHeight - 1, 0)))

        # scrcpy control: x, y, screen_w, screen_h, hscroll (f32), vscroll (f32), buttons
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
