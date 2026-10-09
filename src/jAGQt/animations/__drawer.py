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
    lW = max(0, int(width))
    target.setMinimumWidth(lW)
    target.setMaximumWidth(lW)
    target.setFixedWidth(lW)


# ==================================================================================
class DrawerAnimation(AnimationBase):
    """Smooth width roll in/out via setFixedWidth (layout-visible)."""

    def __init__(
        self,
        target: Optional[QWidget] = None,
        startWidth: int = 0,
        endWidth: int = 240,
        durationMs: int = 280,
        easing: QEasingCurve.Type = QEasingCurve.Type.InOutCubic,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(target=target, durationMs=durationMs, easing=easing, parent=parent)
        self._startWidth: int = int(startWidth)
        self._endWidth: int = int(endWidth)
        self._anim: Optional[QVariantAnimation] = None

    def SetRange(self, startWidth: int, endWidth: int) -> None:
        self._startWidth = int(startWidth)
        self._endWidth = int(endWidth)

    def _onStart(self) -> None:
        if self._target is None:
            self._emitFinished()
            return

        lLo = min(self._startWidth, self._endWidth)
        lHi = max(self._startWidth, self._endWidth)
        self._target.setMinimumWidth(max(0, lLo))
        self._target.setMaximumWidth(max(lHi, 1))

        self._anim = QVariantAnimation(self)
        self._anim.setDuration(self._durationMs)
        self._anim.setEasingCurve(self._easing)
        self._anim.setStartValue(float(self._startWidth))
        self._anim.setEndValue(float(self._endWidth))
        self._anim.valueChanged.connect(self._onValue)
        self._anim.finished.connect(self._onAnimFinished)
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
