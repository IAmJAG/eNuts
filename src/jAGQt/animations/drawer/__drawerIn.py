# ==================================================================================
from __future__ import annotations

# ==================================================================================
from jAGQt.utilities import AnimationError

# ==================================================================================
from .__drawerAnimationBase import DrawerAnimationBase
from .__eDrawerDirection import eDrawerDirection


# ==================================================================================
class DrawerIn(DrawerAnimationBase):
    """Expand the widget along the drawer direction.

    ``start(endWidth=200)`` or ``start(endHeight=...)`` required for the
    animated axis. Optional ``startWidth`` / ``startHeight`` override the
    captured current size before the run.
    """

    def _onStart(self, *args, **kwargs) -> None:
        d = self._direction
        if d in (eDrawerDirection.Left, eDrawerDirection.Right):
            endWidth = kwargs.get("endWidth")
            if endWidth is None and args:
                endWidth = args[0]
            endHeight = None
            if endWidth is None:
                raise AnimationError("DrawerIn requires endWidth for horizontal drawer")
        else:
            endHeight = kwargs.get("endHeight")
            if endHeight is None and args:
                endHeight = args[0]
            endWidth = None
            if endHeight is None:
                raise AnimationError("DrawerIn requires endHeight for vertical drawer")

        self._resolveEndSize(
            endWidth=endWidth, endHeight=endHeight, collapsed=False
        )

        startWidth = kwargs.get("startWidth")
        startHeight = kwargs.get("startHeight")
        if startWidth is not None or startHeight is not None:
            from PySide6.QtCore import QSize

            w = int(startWidth) if startWidth is not None else self._startSize.width()
            h = int(startHeight) if startHeight is not None else self._startSize.height()
            self._startSize = QSize(max(0, w), max(0, h))
            self._applySize(self._startSize)
        else:
            self._applySize(self._startSize)
