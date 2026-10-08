# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtCore import (
    QAbstractAnimation,
    QEasingCurve,
    QObject,
    QPropertyAnimation,
    QSequentialAnimationGroup,
)
from PySide6.QtWidgets import QWidget

# ==================================================================================
from .__base import AnimationBase


# ==================================================================================
class RubberBandAnimation(AnimationBase):
    """Overshoot then settle on maximumWidth. Any QWidget."""

    def __init__(
        self,
        target: Optional[QWidget] = None,
        startWidth: int = 0,
        endWidth: int = 240,
        overshootPx: int = 18,
        durationMs: int = 280,
        easing: QEasingCurve.Type = QEasingCurve.Type.OutCubic,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(target=target, durationMs=durationMs, easing=easing, parent=parent)
        self._startWidth: int = int(startWidth)
        self._endWidth: int = int(endWidth)
        self._overshootPx: int = max(0, int(overshootPx))
        self._group: Optional[QSequentialAnimationGroup] = None

    def SetRange(self, startWidth: int, endWidth: int, overshootPx: int = 18) -> None:
        self._startWidth = int(startWidth)
        self._endWidth = int(endWidth)
        self._overshootPx = max(0, int(overshootPx))

    def _onStart(self) -> None:
        if self._target is None:
            self._emitFinished()
            return

        lDirection: int = 1 if self._endWidth >= self._startWidth else -1
        lPeak: int = self._endWidth + (self._overshootPx * lDirection)

        lFirst = QPropertyAnimation(self._target, b"maximumWidth")
        lFirst.setDuration(int(self._durationMs * 0.65))
        lFirst.setEasingCurve(QEasingCurve.Type.OutCubic)
        lFirst.setStartValue(self._startWidth)
        lFirst.setEndValue(lPeak)

        lSecond = QPropertyAnimation(self._target, b"maximumWidth")
        lSecond.setDuration(int(self._durationMs * 0.35))
        lSecond.setEasingCurve(QEasingCurve.Type.InOutCubic)
        lSecond.setStartValue(lPeak)
        lSecond.setEndValue(self._endWidth)

        self._group = QSequentialAnimationGroup(self)
        self._group.addAnimation(lFirst)
        self._group.addAnimation(lSecond)
        self._group.finished.connect(self._onAnimFinished)
        self._target.setMinimumWidth(min(self._startWidth, self._endWidth, lPeak))
        self._group.start()

    def _onStop(self) -> None:
        if self._group is not None:
            self._group.stop()
            self._group = None

    def _onAnimFinished(self) -> None:
        self._group = None
        if self._target is not None:
            self._target.setFixedWidth(self._endWidth)
        self._emitFinished()
