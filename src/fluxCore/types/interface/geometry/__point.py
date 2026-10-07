# ==================================================================================
# src/fluxCore/actions/__point.py
# ==================================================================================
from typing import Protocol


# ==================================================================================
class iPoint(Protocol):    
    @property
    def x(self) -> float | int: ...
    @property
    def y(self) -> float | int: ...
    @property
    def top(self) -> float | int: ...
    @property
    def left(self) -> float | int: ...
    @property
    def rngRadius(self) -> float | int: ...
    
    def randomPoint(self, rngRadius: float | int | None = None) -> "iPoint": ...