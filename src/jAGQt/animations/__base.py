# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtCore import QEasingCurve, QObject, Signal
from PySide6.QtWidgets import QWidget


# ==================================================================================
class AnimationBase(QObject):
    """Flexible base for widget animations. Not frozen — extend per effect."""

    Finished = Signal()

    def __init__(
        self,
        target: Optional[QWidget] = None,
        durationMs: int = 220,
        easing: QEasingCurve.Type = QEasingCurve.Type.OutCubic,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)
        self._target: Optional[QWidget] = target
        self._durationMs: int = max(0, int(durationMs))
        self._easing: QEasingCurve.Type = easing
        self._running: bool = False

    @property
    def Target(self) -> Optional[QWidget]:
        return self._target

    @Target.setter
    def Target(self, value: Optional[QWidget]) -> None:
        self._target = value

    @property
    def DurationMs(self) -> int:
        return self._durationMs

    @DurationMs.setter
    def DurationMs(self, value: int) -> None:
        self._durationMs = max(0, int(value))

    @property
    def IsRunning(self) -> bool:
        return self._running

    def Start(self) -> None:
        if self._target is None:
            return
        if self._running:
            self.Stop()
        self._running = True
        self._onStart()

    def Stop(self) -> None:
        if not self._running:
            return
        self._onStop()
        self._running = False

    def _onStart(self) -> None:
        raise NotImplementedError

    def _onStop(self) -> None:
        pass

    def _emitFinished(self) -> None:
        self._running = False
        self.Finished.emit()
