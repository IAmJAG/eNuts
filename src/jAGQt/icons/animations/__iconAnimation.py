# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtCore import QEasingCurve, QObject, Signal, SignalInstance
from PySide6.QtWidgets import QWidget

# ==================================================================================
QECurveType = QEasingCurve.Type
# ==================================================================================


# ==================================================================================
class iIconAnimation(QObject):
    onStart: SignalInstance = Signal("iIconAnimation")
    onStop: SignalInstance = Signal("iIconAnimation")
    onFinished: SignalInstance = Signal("iIconAnimation")
    def __init__(
        self, target: Optional[QWidget], durationMs: int = 180,
        easing: QECurveType = QECurveType.InOutCubic, *args, **kwargs
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
            warning(f"[{self.__class__.__name__}]IconAnimation: already running")
            return
        self._running = True
        self.onStart.emit(self)

    def stop(self) -> None:
        if not self._running: 
            warning(f"[{self.__class__.__name__}]IconAnimation: not running")
            return                
        self.onStop.emit(self)
        self._running = False

    def _emitFinished(self) -> None:
        self._running = False
        self.onFinished.emit(self)
