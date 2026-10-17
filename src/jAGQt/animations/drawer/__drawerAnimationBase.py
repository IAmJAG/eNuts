# ==================================================================================
# src/jAGQt/animations/drawer/__drawerAnimationBase.py
# ==================================================================================
from __future__ import annotations

# ==================================================================================
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget

# ==================================================================================
from jAGQt.utilities import AnimationError

# ==================================================================================
from ..__sizeAnimationBase import SizeAnimationBase
from .__eDrawerDirection import eDrawerDirection


# ==================================================================================
class DrawerAnimationBase(SizeAnimationBase):
    """Drawer open/close by animating widget width or height along one edge."""

    def __init__(
        self,
        target: QWidget,
        direction: eDrawerDirection = eDrawerDirection.Left,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(target, *args, **kwargs)
        self._direction: eDrawerDirection = direction

    @property
    def direction(self) -> eDrawerDirection:
        return self._direction

    @direction.setter
    def direction(self, value: eDrawerDirection) -> None:
        self._direction = value

    def _configureAnchors(self) -> None:
        d = self._direction
        self._anchorRight = d is eDrawerDirection.Right
        self._anchorBottom = d is eDrawerDirection.Bottom

    def _resolveEndSize(
        self,
        *,
        endWidth: int | None,
        endHeight: int | None,
        collapsed: bool,
    ) -> QSize:
        self._captureStart()
        self._configureAnchors()
        w = self._startSize.width()
        h = self._startSize.height()

        d = self._direction
        if d in (eDrawerDirection.Left, eDrawerDirection.Right):
            if endWidth is None:
                raise AnimationError(
                    "Drawer along Left/Right requires endWidth "
                    "(or use DrawerIn/Out helpers that supply it)"
                )
            w = max(0, int(endWidth))
        else:
            if endHeight is None:
                raise AnimationError(
                    "Drawer along Top/Bottom requires endHeight"
                )
            h = max(0, int(endHeight))

        self._endSize = QSize(w, h)
        return self._endSize
