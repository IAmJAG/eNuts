# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtCore import QEasingCurve, QObject, Signal, SignalInstance
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget

# ==================================================================================
from jAGFx.logging import warning

# ==================================================================================
from ...types.interface.icons.animation import iIconAnimation
from ...types.interface.widgets.icons import iIcon

# ==================================================================================
QECurveType = QEasingCurve.Type
# ==================================================================================


# ==================================================================================
class IconAnimation(QObject):
    onStart: SignalInstance = Signal(iIconAnimation)
    onStop: SignalInstance = Signal(iIconAnimation)
    onFinished: SignalInstance = Signal(iIconAnimation)
    onProgress: SignalInstance = Signal(iIconAnimation, float)

    def __init__(
        self,  durationMs: int = 180, easing: QECurveType = QECurveType.InOutCubic,
        *args, **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._target: Optional[iIcon] = None
        self._durationMs: int = max(0, int(durationMs))
        self._easing: QEasingCurve.Type = easing
        self._running: bool = False

    @property
    def target(self) -> Optional[iIcon]:
        return self._target

    @target.setter
    def target(self, value: Optional[iIcon]) -> None:
        if value is not None and not isinstance(value, iIcon):
            raise TypeError(f"Invalid target: Expected iIcon, got {type(value).__name__}.")        
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

    def _onProgress(self, value: float) -> None:
        self.onProgress.emit(self, value)

    def _onFinished(self) -> None:
        self._running = False
        self.onFinished.emit(self)

    def _validate(self) -> bool:
        if self._running:
            warning(f"[{self.__class__.__name__}] already running")
            return False

        if self._target is None or not isinstance(self._target, iIcon):
            warning(f"[{self.__class__.__name__}] no valid target")
            return False

        return True

    # ==================================================================================
    def start(self) -> None:
        if not self._validate():
            self._onFinished()
            return
        
        self._running = True
        self.onStart.emit(self)

    def stop(self) -> None:
        if not self._running:
            warning(f"[{self.__class__.__name__}] not running")
            return
        
        self.onStop.emit(self)
        self._onFinished()