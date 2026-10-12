# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Protocol, runtime_checkable

# ==================================================================================
from PySide6.QtCore import QEasingCurve

# ==================================================================================
CurveType = QEasingCurve.Type
# ==================================================================================

# ==================================================================================
@runtime_checkable
class iAnimated(Protocol):
    def __init__(
        self, durationMs: int = 220, easing: CurveType = CurveType.OutCubic,
        *args, **kwargs,
    ) -> None: ...
        
    @property
    def durationMs(self) -> int: ...
    @property
    def isRunning(self) -> bool: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def _onStart(self) -> None: ...
    def _onStop(self) -> None: ...
    def _emitFinished(self) -> None: ...
