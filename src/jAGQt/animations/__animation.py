# ==================================================================================
from __future__ import annotations

# ==================================================================================
from PySide6.QtCore import QEasingCurve, Signal, SignalInstance
from PySide6.QtWidgets import QWidget

# ==================================================================================
CurveType = QEasingCurve.Type
# ==================================================================================

# ==================================================================================
class Animation:
    OBJECT_NAME = "W_ANIMATED"
    Finished: SignalInstance = Signal()    
    def __init__(
        self, target: QWidget, durationMs: int = 220,
        easing: CurveType = CurveType.OutCubic,
        *args, **kwargs
    ) -> None:
        OBJNAME = "W_ANIMATED"
        super().__init__(objectName=OBJNAME, *args, **kwargs)
        self._target: QWidget = target
        self._durationMs: int = max(0, int(durationMs))
        self._easing: QEasingCurve.Type = easing
        self._running: bool = False

    @property
    def durationMs(self) -> int: 
        return self._durationMs
    
    @property
    def isRunning(self) -> bool: 
        return self._running
    
    def start(self) -> None: 
        if self._running: self.stop()
        self._running = True
        self._onStart()

    def stop(self) -> None: 
        if not self._running: return        
        self._onStop()
        self._running = False

    def _onStart(self) -> None: 
        self._running = False

    def _onStop(self) -> None:
        pass

    def _emitFinished(self) -> None: 
        self._running = False
        self.Finished.emit()
