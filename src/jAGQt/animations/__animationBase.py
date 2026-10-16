# ==================================================================================
# src/jAGQt/animations/__animationBase.py
# ==================================================================================
from __future__ import annotations

# ==================================================================================
from abc import ABC, abstractmethod
from traceback import format_exc
from typing import Optional

# ==================================================================================
from PySide6.QtCore import (
    QAbstractAnimation,
    QEasingCurve,
    QObject,
    QVariantAnimation,
    Signal,
)

from jAGFx.workflow import workflow

# ==================================================================================
from jAGQt.types.interface.animations import iAnimation
from jAGQt.utilities import AnimationError

# ==================================================================================
C_DEFAULT_DURATION_MS = 220
# ==================================================================================


# ==================================================================================
@workflow
class AnimationBase(QObject, ABC):
    started = Signal()
    finished = Signal()
    stopped = Signal()
    def __init__(
        self, durationMs: int = C_DEFAULT_DURATION_MS,
        easing: QEasingCurve.Type = QEasingCurve.Type.OutCubic,
        *args, **kwargs,
    ) -> None:        
        if durationMs < 0:
            raise AnimationError(f"durationMs must be >= 0, got {durationMs}")

        super().__init__(*args, **kwargs)
        self._durationMs: int = int(durationMs)
        self._easing: QEasingCurve.Type = easing        

    def _wIntializeDriver(self) -> None:
        self._driver: QVariantAnimation = QVariantAnimation(self)
        self._driver.setStartValue(0.0)
        self._driver.setEndValue(1.0)
        self._driver.setDuration(self._durationMs)
        self._driver.setEasingCurve(self._easing)
        self._driver.valueChanged.connect(self._onValueChanged)
        self._driver.finished.connect(self._onDriverFinished)

    # ==================================================================================
    @property
    def isRunning(self) -> bool:
        return self._driver.state() == QAbstractAnimation.State.Running

    @property
    def durationMs(self) -> int:
        return self._durationMs

    @durationMs.setter
    def durationMs(self, value: int) -> None:
        if value < 0:
            raise AnimationError(f"durationMs must be >= 0, got {value}")
        self._durationMs = int(value)
        self._driver.setDuration(self._durationMs)

    @property
    def easing(self) -> QEasingCurve.Type:
        return self._easing

    @easing.setter
    def easing(self, value: QEasingCurve.Type) -> None:
        self._easing = value
        self._driver.setEasingCurve(value)

    # ==================================================================================
    def start(self) -> None:
        try:
            if self.isRunning: self.stop()
            self._onStart()
            self._driver.setCurrentTime(0)
            self._driver.start()
            self.started.emit()

        except Exception as ex:
            error("[AnimationBase] start FAIL", ex)
            error(f"[AnimationBase] start traceback:\n{format_exc()}")
            raise

    def stop(self) -> None:
        try:
            if not self.isRunning: return
            self._driver.stop()
            self._onStop()
            self.stopped.emit()

        except Exception as ex:
            error("[AnimationBase] stop FAIL", ex)
            error(f"[AnimationBase] stop traceback:\n{format_exc()}")
            raise

    # ==================================================================================
    def _onValueChanged(self, value: object) -> None:
        try:
            progress = float(value)
            self._onProgress(progress)

        except Exception as ex:
            error("[AnimationBase] _onValueChanged FAIL", ex)
            error(f"[AnimationBase] _onValueChanged traceback:\n{format_exc()}")
            self.stop()
            raise

    def _onDriverFinished(self) -> None:
        try:
            self._onProgress(1.0)
            self._onFinished()
            self.finished.emit()
            
        except Exception as ex:
            error("[AnimationBase] _onDriverFinished FAIL", ex)
            error(f"[AnimationBase] _onDriverFinished traceback:\n{format_exc()}")
            raise

    def _onStart(self) -> None:
        """Hook invoked immediately before the driver starts."""

    def _onStop(self) -> None:
        """Hook invoked after the driver is stopped early."""

    def _onFinished(self) -> None:
        """Hook invoked after a full run reaches progress 1.0."""

    @abstractmethod
    def _onProgress(self, progress: float) -> None:
        """Apply a frame for *progress* in ``[0.0, 1.0]``."""


# Structural check against the contract (not inheritance — Protocol).
def _assertProtocol() -> None:
    _: type[iAnimation] = AnimationBase  # type: ignore[assignment]
