# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtCore import QEasingCurve, QObject, Signal, SignalInstance
from PySide6.QtWidgets import QWidget

# ==================================================================================
from jAGFx.logging import warning

# ==================================================================================
QECurveType = QEasingCurve.Type
# ==================================================================================


# ==================================================================================
class IconAnimation(QObject):
    """Base for square-icon transitions (morph, transpose, etc.)."""

    onStart: SignalInstance = Signal(object)
    onStop: SignalInstance = Signal(object)
    onFinished: SignalInstance = Signal(object)

    def __init__(
        self,
        target: Optional[QWidget] = None,
        durationMs: int = 180,
        easing: QECurveType = QECurveType.InOutCubic,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._target: Optional[QWidget] = target
        self._durationMs: int = max(0, int(durationMs))
        self._easing: QEasingCurve.Type = easing
        self._running: bool = False

    @property
    def target(self) -> Optional[QWidget]:
        return self._target

    @target.setter
    def target(self, value: Optional[QWidget]) -> None:
        self._target = value

    @property
    def durationMs(self) -> int:
        return self._durationMs

    @durationMs.setter
    def durationMs(self, value: int) -> None:
        self._durationMs = max(0, int(value))

    @property
    def isRunning(self) -> bool:
        return self._running

    # ==================================================================================
    def start(self) -> None:
        if self._running:
            warning(f"[{self.__class__.__name__}] already running")
            return
        self._running = True
        self.onStart.emit(self)
        self._onStart()

    def stop(self) -> None:
        if not self._running:
            warning(f"[{self.__class__.__name__}] not running")
            return
        self._onStop()
        self.onStop.emit(self)
        self._running = False

    def _onStart(self) -> None:
        """Subclass hook — start the concrete transition."""
        self._emitFinished()

    def _onStop(self) -> None:
        """Subclass hook — abort any in-flight transition."""
        pass

    def _emitFinished(self) -> None:
        self._running = False
        self.onFinished.emit(self)
