# ==================================================================================
# src/jAGQt/animations/__animationBase.py
# ==================================================================================
from __future__ import annotations

# ==================================================================================
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
from jAGQt.utilities import AnimationError

# ==================================================================================
C_DEFAULT_DURATION_MS = 220
# ==================================================================================


# ==================================================================================
# QObject uses a Shiboken metaclass; do not mix with ABC (ABCMeta conflict).
# Subclasses must override _onProgress; the base raises NotImplementedError.
# ==================================================================================
@workflow
class AnimationBase(QObject):
    started = Signal()
    finished = Signal()
    stopped = Signal()

    def __init__(
        self,
        durationMs: int = C_DEFAULT_DURATION_MS,
        easing: QEasingCurve.Type = QEasingCurve.Type.OutCubic,
        *args,
        **kwargs,
    ) -> None:
        if durationMs < 0:
            raise AnimationError(f"durationMs must be >= 0, got {durationMs}")

        super().__init__(*args, **kwargs)
        self._durationMs: int = int(durationMs)
        self._easing: QEasingCurve.Type = easing
        self._driver: Optional[QVariantAnimation] = None

    def _wInitializeDriver(self) -> None:
        driver: QVariantAnimation = QVariantAnimation(self)
        driver.setStartValue(0.0)
        driver.setEndValue(1.0)
        driver.setDuration(self._durationMs)
        driver.setEasingCurve(self._easing)
        driver.valueChanged.connect(self._onValueChanged)
        driver.finished.connect(self._onDriverFinished)
        driver.setParent(self)
        self._driver = driver

    def _ensureDriver(self) -> QVariantAnimation:
        if self._driver is None:
            self._wInitializeDriver()
        assert self._driver is not None
        return self._driver

    # ==================================================================================
    @property
    def isRunning(self) -> bool:
        driver = self._driver
        if driver is None:
            return False
        return driver.state() == QAbstractAnimation.State.Running

    @property
    def durationMs(self) -> int:
        return self._durationMs

    @durationMs.setter
    def durationMs(self, value: int) -> None:
        if value < 0:
            raise AnimationError(f"durationMs must be >= 0, got {value}")
        self._durationMs = int(value)
        if self._driver is not None:
            self._driver.setDuration(self._durationMs)

    @property
    def easing(self) -> QEasingCurve.Type:
        return self._easing

    @easing.setter
    def easing(self, value: QEasingCurve.Type) -> None:
        self._easing = value
        if self._driver is not None:
            self._driver.setEasingCurve(value)

    # ==================================================================================
    def start(self, *args, **kwargs) -> None:
        try:
            if self.isRunning:
                self.stop()
            driver = self._ensureDriver()
            self._onStart(*args, **kwargs)
            driver.setCurrentTime(0)
            driver.start()
            self.started.emit()

        except Exception as ex:
            error("[AnimationBase] start FAIL", ex)
            error(f"[AnimationBase] start traceback:\n{format_exc()}")
            raise

    def stop(self) -> None:
        try:
            if not self.isRunning:
                return
            driver = self._ensureDriver()
            driver.stop()
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

    def _onStart(self, *args, **kwargs) -> None:
        """Hook invoked immediately before the driver starts."""

    def _onStop(self) -> None:
        """Hook invoked after the driver is stopped early."""

    def _onFinished(self) -> None:
        """Hook invoked after a full run reaches progress 1.0."""

    def _onProgress(self, progress: float) -> None:
        """Apply a frame for *progress* in ``[0.0, 1.0]``. Subclasses must override."""
        raise NotImplementedError(
            f"{type(self).__name__} must implement _onProgress(progress)"
        )
