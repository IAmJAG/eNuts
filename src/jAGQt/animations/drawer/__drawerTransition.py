# ==================================================================================
from __future__ import annotations

# ==================================================================================
from PySide6.QtCore import QSize

# ==================================================================================
from jAGQt.utilities import AnimationError

# ==================================================================================
from .__drawerAnimationBase import DrawerAnimationBase
from .__eDrawerDirection import eDrawerDirection


# ==================================================================================
class DrawerTransition(DrawerAnimationBase):
    """Animate widget size from current (or explicit start) to end along direction.

    ``start(endWidth=..., endHeight=optional, startWidth=optional, startHeight=optional)``
    Horizontal directions require ``endWidth``; vertical require ``endHeight``.
    """

    def _onStart(self, *args, **kwargs) -> None:
        d = self._direction
        endWidth = kwargs.get("endWidth")
        endHeight = kwargs.get("endHeight")
        if endWidth is None and d in (eDrawerDirection.Left, eDrawerDirection.Right):
            if args:
                endWidth = args[0]
        if endHeight is None and d in (eDrawerDirection.Top, eDrawerDirection.Bottom):
            if args:
                endHeight = args[0]

        if d in (eDrawerDirection.Left, eDrawerDirection.Right) and endWidth is None:
            raise AnimationError("DrawerTransition requires endWidth")
        if d in (eDrawerDirection.Top, eDrawerDirection.Bottom) and endHeight is None:
            raise AnimationError("DrawerTransition requires endHeight")

        self._resolveEndSize(
            endWidth=endWidth, endHeight=endHeight, collapsed=False
        )

        startWidth = kwargs.get("startWidth")
        startHeight = kwargs.get("startHeight")
        if startWidth is not None or startHeight is not None:
            w = int(startWidth) if startWidth is not None else self._startSize.width()
            h = int(startHeight) if startHeight is not None else self._startSize.height()
            self._startSize = QSize(max(0, w), max(0, h))

        self._applySize(self._startSize)
