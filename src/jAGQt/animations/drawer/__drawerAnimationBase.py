# ==================================================================================
# src/jAGQt/animations/drawer/__drawerAnimationBase.py
# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QWidget

# ==================================================================================
from ..__animationBase import AnimationBase
from ..__pixmapUtils import (
    ImageLike,
    applyPixmap,
    assertSetPixmap,
    grabWidget,
    scaleToTarget,
    toPixmap,
)
from .__eDrawerDirection import eDrawerDirection


# ==================================================================================
class DrawerAnimationBase(AnimationBase):
    """Slide content like a drawer; paint via grab + setPixmap."""

    def __init__(
        self,
        target: QWidget,
        direction: eDrawerDirection = eDrawerDirection.Left,
        *args,
        **kwargs,
    ) -> None:
        assertSetPixmap(target)
        super().__init__(*args, **kwargs)
        self._target: QWidget = target
        self._direction: eDrawerDirection = direction
        self._original: QPixmap = QPixmap()
        self._content: QPixmap = QPixmap()

    @property
    def direction(self) -> eDrawerDirection:
        return self._direction

    @direction.setter
    def direction(self, value: eDrawerDirection) -> None:
        self._direction = value

    def _grabTarget(self) -> QPixmap:
        return grabWidget(self._target)

    def _applyPixmap(self, pixmap: QPixmap) -> None:
        applyPixmap(self._target, pixmap)

    def _buildFrame(
        self,
        progress: float,
        underneath: QPixmap,
        sliding: QPixmap,
        *,
        slideIn: bool,
    ) -> QPixmap:
        """slideIn=True: sliding enters covering underneath; False: sliding exits."""
        progress = max(0.0, min(1.0, progress))
        w = max(1, self._target.width())
        h = max(1, self._target.height())
        frame = QPixmap(w, h)
        frame.fill(Qt.GlobalColor.transparent)

        under = scaleToTarget(underneath, self._target) if not underneath.isNull() else QPixmap()
        slide = scaleToTarget(sliding, self._target) if not sliding.isNull() else QPixmap()

        painter = QPainter(frame)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        if not under.isNull():
            painter.drawPixmap(0, 0, under)

        if not slide.isNull():
            ox, oy = self._offset(w, h, progress, slideIn=slideIn)
            painter.drawPixmap(int(ox), int(oy), slide)

        painter.end()
        return frame

    def _offset(
        self, w: int, h: int, progress: float, *,
        slideIn: bool,
    ) -> tuple[float, float]:
        # progress 0 → fully off-screen (in) or fully on (out)
        # progress 1 → fully on (in) or fully off (out)
        t = progress if slideIn else (1.0 - progress)
        d = self._direction
        if d is eDrawerDirection.Left:
            return (-w * (1.0 - t), 0.0)
        if d is eDrawerDirection.Right:
            return (w * (1.0 - t), 0.0)
        if d is eDrawerDirection.Top:
            return (0.0, -h * (1.0 - t))
        return (0.0, h * (1.0 - t))
