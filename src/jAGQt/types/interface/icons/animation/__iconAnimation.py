# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional, Protocol, runtime_checkable

# ==================================================================================
from PySide6.QtCore import QEasingCurve, QObject, Signal, SignalInstance
from PySide6.QtWidgets import QWidget

# ==================================================================================
QECurveType = QEasingCurve.Type
# ==================================================================================


# ==================================================================================
@runtime_checkable
class iIconAnimation(Protocol):
    onStart: SignalInstance
    onStop: SignalInstance
    onFinished: SignalInstance
    def __init__(
        self, target: Optional[QWidget], durationMs: int = 180, 
        easing: QECurveType = QECurveType.InOutCubic,
        *args, **kwargs
    ) -> None: ...

    @property
    def target(self) -> Optional[QWidget]: ...
    @property
    def durationMs(self) -> int: ...
    @property
    def isRunning(self) -> bool: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...
