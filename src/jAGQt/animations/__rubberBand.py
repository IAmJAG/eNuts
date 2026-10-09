# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtCore import QEasingCurve, QObject, QVariantAnimation
from PySide6.QtWidgets import QWidget

# ==================================================================================
from .__base import AnimationBase


# ==================================================================================
def _applyWidth(target: QWidget, width: int) -> None:
    """Drive real width. maximumWidth alone is ignored when fixedWidth is set."""
    lW = max(0, int(width))
    target.setMinimumWidth(lW)
    target.setMaximumWidth(lW)
    target.setFixedWidth(lW)


# ==================================================================================
class RubberBandAnimation(AnimationBase):
    """Width rubber-band: overshoot past the target, undershoot, then settle.

    Uses keyframed QVariantAnimation + setFixedWidth so the layout actually moves
    (QPropertyAnimation on maximumWidth alone does not when fixedWidth is locked).
    """

    def __init__(
        self,
        target: Optional[QWidget] = None,
        startWidth: int = 0,
        endWidth: int = 240,
        overshootPx: int = 28,
        undershootPx: int = 10,
        durationMs: int = 420,
        easing: QEasingCurve.Type = QEasingCurve.Type.OutCubic,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(target=target, durationMs=durationMs, easing=easing, parent=parent)
        self._startWidth: int = int(startWidth)
        self._endWidth: int = int(endWidth)
        self._overshootPx: int = max(0, int(overshootPx))
        self._undershootPx: int = max(0, int(undershootPx))
        self._anim: Optional[QVariantAnimation] = None

    def SetRange(
        self,
        startWidth: int,
        endWidth: int,
        overshootPx: int = 28,
        undershootPx: int = 10,
    ) -> None:
        self._startWidth = int(startWidth)
        self._endWidth = int(endWidth)
        self._overshootPx = max(0, int(overshootPx))
        self._undershootPx = max(0, int(undershootPx))

    def _onStart(self) -> None:
        if self._target is None:
            self._emitFinished()
            return

        lStart = self._startWidth
        lEnd = self._endWidth
        lDir = 1 if lEnd >= lStart else -1
        lPeak = lEnd + (self._overshootPx * lDir)
        lDip = lEnd - (self._undershootPx * lDir)

        # Keep dip on the legal side of zero for collapse
        if lDir < 0:
            lPeak = max(0, lPeak)
            lDip = max(0, lDip)

        self._anim = QVariantAnimation(self)
        self._anim.setDuration(self._durationMs)
        self._anim.setEasingCurve(QEasingCurve.Type.Linear)

        # Keyframes: accelerate out → overshoot → snap past → settle
        self._anim.setKeyValueAt(0.00, float(lStart))
        self._anim.setKeyValueAt(0.55, float(lPeak))
        self._anim.setKeyValueAt(0.78, float(lDip))
        self._anim.setKeyValueAt(1.00, float(lEnd))

        self._anim.valueChanged.connect(self._onValue)
        self._anim.finished.connect(self._onAnimFinished)

        # Unlock width so intermediate frames can move freely
        lLo = min(lStart, lEnd, lPeak, lDip)
        lHi = max(lStart, lEnd, lPeak, lDip)
        self._target.setMinimumWidth(max(0, lLo))
        self._target.setMaximumWidth(max(lHi, 1))

        self._anim.start()

    def _onValue(self, value: object) -> None:
        if self._target is None:
            return
        _applyWidth(self._target, int(round(float(value))))

    def _onStop(self) -> None:
        if self._anim is not None:
            self._anim.stop()
            self._anim = None

    def _onAnimFinished(self) -> None:
        self._anim = None
        if self._target is not None:
            _applyWidth(self._target, self._endWidth)
        self._emitFinished()
