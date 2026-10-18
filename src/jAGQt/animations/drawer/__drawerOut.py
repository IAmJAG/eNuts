# ==================================================================================
from __future__ import annotations

# ==================================================================================
from jAGQt.utilities import AnimationError

# ==================================================================================
from .__drawerAnimationBase import DrawerAnimationBase
from .__eDrawerDirection import eDrawerDirection


# ==================================================================================
class DrawerOut(DrawerAnimationBase):
    """Collapse the widget along the drawer direction.

    ``start(endWidth=0)`` or ``start(endHeight=0)`` depending on direction.
    Defaults to fully collapsed (0) on the animated axis.
    """

    def _onStart(self, *args, **kwargs) -> None:
        d = self._direction
        if d in (eDrawerDirection.Left, eDrawerDirection.Right):
            endWidth = kwargs.get("endWidth", 0)
            endHeight = None
        else:
            endWidth = None
            endHeight = kwargs.get("endHeight", 0)

        if d in (eDrawerDirection.Left, eDrawerDirection.Right) and endWidth is None:
            raise AnimationError("DrawerOut requires endWidth for horizontal drawer")
        if d in (eDrawerDirection.Top, eDrawerDirection.Bottom) and endHeight is None:
            raise AnimationError("DrawerOut requires endHeight for vertical drawer")

        self._resolveEndSize(
            endWidth=endWidth, endHeight=endHeight, collapsed=True
        )
        self._applySize(self._startSize)
