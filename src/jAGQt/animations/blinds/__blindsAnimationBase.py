# ==================================================================================
# src/jAGQt/animations/blinds/__blindsAnimationBase.py
# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import QWidget

# ==================================================================================
from ..__animationBase import AnimationBase
from ..__pixmapUtils import (
    applyPixmap,
    assertSetPixmap,
    grabWidget,
    scaleToTarget,
)
from .__eBlindsOrientation import eBlindsOrientation

# ==================================================================================
C_DEFAULT_STRIPS = 8
# ==================================================================================


# ==================================================================================
class BlindsAnimationBase(AnimationBase):
    """Window-blinds style strip reveal; paint via grab + setPixmap."""

    def __init__(
        self,
        target: QWidget,
        orientation: eBlindsOrientation = eBlindsOrientation.Horizontal,
        stripCount: int = C_DEFAULT_STRIPS,
        *args,
        **kwargs,
    ) -> None:
        assertSetPixmap(target)
        if stripCount < 1:
            stripCount = 1
        super().__init__(*args, **kwargs)
        self._target: QWidget = target
        self._orientation: eBlindsOrientation = orientation
        self._stripCount: int = int(stripCount)
        self._original: QPixmap = QPixmap()
        self._content: QPixmap = QPixmap()

    @property
    def orientation(self) -> eBlindsOrientation:
        return self._orientation

    @orientation.setter
    def orientation(self, value: eBlindsOrientation) -> None:
        self._orientation = value

    @property
    def stripCount(self) -> int:
        return self._stripCount

    @stripCount.setter
    def stripCount(self, value: int) -> None:
        self._stripCount = max(1, int(value))

    def _grabTarget(self) -> QPixmap:
        return grabWidget(self._target)

    def _applyPixmap(self, pixmap: QPixmap) -> None:
        applyPixmap(self._target, pixmap)

    def _buildFrame(
        self,
        progress: float,
        underneath: QPixmap,
        revealed: QPixmap,
    ) -> QPixmap:
        """Each strip opens from 0→full along its short axis as progress advances."""
        progress = max(0.0, min(1.0, progress))
        w = max(1, self._target.width())
        h = max(1, self._target.height())
        frame = QPixmap(w, h)
        frame.fill(Qt.GlobalColor.transparent)

        under = scaleToTarget(underneath, self._target) if not underneath.isNull() else QPixmap()
        over = scaleToTarget(revealed, self._target) if not revealed.isNull() else QPixmap()

        painter = QPainter(frame)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        if not under.isNull():
            painter.drawPixmap(0, 0, under)

        n = self._stripCount
        horizontal = self._orientation is eBlindsOrientation.Horizontal

        for i in range(n):
            if horizontal:
                stripH = h / n
                y0 = i * stripH
                openH = stripH * progress
                src = QRectF(0, y0, w, openH)
                dst = QRectF(0, y0, w, openH)
            else:
                stripW = w / n
                x0 = i * stripW
                openW = stripW * progress
                src = QRectF(x0, 0, openW, h)
                dst = QRectF(x0, 0, openW, h)

            if src.width() <= 0 or src.height() <= 0:
                continue

            painter.save()
            painter.setClipRect(dst)
            if not over.isNull():
                painter.drawPixmap(0, 0, over)
            else:
                painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
                painter.fillRect(dst, Qt.GlobalColor.transparent)
            painter.restore()

        painter.end()
        return frame
