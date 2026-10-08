# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtCore import QEasingCurve, QObject, QPropertyAnimation
from PySide6.QtWidgets import QWidget

# ==================================================================================
from .__base import AnimationBase


# ==================================================================================
class DrawerAnimation(AnimationBase):
    """Animate a widget's maximumWidth (panel drawer open/close). Any QWidget."""

    def __init__(
        self,
        target: Optional[QWidget] = None,
        startWidth: int = 0,
        endWidth: int = 240,
        durationMs: int = 220,
        easing: QEasingCurve.Type = QEasingCurve.Type.InOutCubic,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(target=target, durationMs=durationMs, easing=easing, parent=parent)
        self._startWidth: int = int(startWidth)
        self._endWidth: int = int(endWidth)
        self._anim: Optional[QPropertyAnimation] = None

    def SetRange(self, startWidth: int, endWidth: int) -> None:
        self._startWidth = int(startWidth)
        self._endWidth = int(endWidth)

    def _onStart(self) -> None:
        if self._target is None:
            self._emitFinished()
            return
        self._anim = QPropertyAnimation(self._target, b"maximumWidth", self)
        self._anim.setDuration(self._durationMs)
        self._anim.setEasingCurve(self._easing)
        self._anim.setStartValue(self._startWidth)
        self._anim.setEndValue(self._endWidth)
        self._anim.finished.connect(self._onAnimFinished)
        self._target.setMinimumWidth(min(self._startWidth, self._endWidth))
        self._anim.start()

    def _onStop(self) -> None:
        if self._anim is not None:
            self._anim.stop()
            self._anim = None

    def _onAnimFinished(self) -> None:
        self._anim = None
        if self._target is not None:
            self._target.setFixedWidth(self._endWidth)
        self._emitFinished()
