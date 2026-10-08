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
class RollAnimation(AnimationBase):
    """Roll up / roll down via maximumHeight. Any QWidget."""

    def __init__(
        self,
        target: Optional[QWidget] = None,
        startHeight: int = 0,
        endHeight: int = 0,
        durationMs: int = 180,
        easing: QEasingCurve.Type = QEasingCurve.Type.OutCubic,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(target=target, durationMs=durationMs, easing=easing, parent=parent)
        self._startHeight: int = int(startHeight)
        self._endHeight: int = int(endHeight)
        self._anim: Optional[QPropertyAnimation] = None

    def SetRange(self, startHeight: int, endHeight: int) -> None:
        self._startHeight = int(startHeight)
        self._endHeight = int(endHeight)

    def RollDown(self, endHeight: int) -> None:
        if self._target is None:
            return
        self._startHeight = self._target.height() if self._target.isVisible() else 0
        self._endHeight = int(endHeight)
        self.Start()

    def RollUp(self) -> None:
        if self._target is None:
            return
        self._startHeight = self._target.height()
        self._endHeight = 0
        self.Start()

    def _onStart(self) -> None:
        if self._target is None:
            self._emitFinished()
            return
        self._target.setVisible(True)
        self._anim = QPropertyAnimation(self._target, b"maximumHeight", self)
        self._anim.setDuration(self._durationMs)
        self._anim.setEasingCurve(self._easing)
        self._anim.setStartValue(self._startHeight)
        self._anim.setEndValue(self._endHeight)
        self._anim.finished.connect(self._onAnimFinished)
        self._anim.start()

    def _onStop(self) -> None:
        if self._anim is not None:
            self._anim.stop()
            self._anim = None

    def _onAnimFinished(self) -> None:
        self._anim = None
        if self._target is not None:
            if self._endHeight <= 0:
                self._target.setMaximumHeight(0)
                self._target.setVisible(False)
            else:
                self._target.setMaximumHeight(16777215)
                self._target.setVisible(True)
        self._emitFinished()
