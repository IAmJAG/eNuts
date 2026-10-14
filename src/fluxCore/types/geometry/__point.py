# ==================================================================================
# src/fluxCore/actions/__point.py
# ==================================================================================
import random

# ==================================================================================
from typing import runtime_checkable

# ==================================================================================
from jAGFx.serializer import Serializeable

# ==================================================================================
from ..contracts.geometry import iGeometry, iPoint


# ==================================================================================
class Point(Serializeable):
    def __init__(self, x: float | int, y: float | int, rngRadius: float | int = 5.0):
        super().__init__()
        self._x: float | int = float(x)
        self._y: float | int = float(y)
        self._rngRadius: float | int = float(rngRadius)
        self.Properties.extend(["x", "y"])

# region [PROPERTIES]
    @property
    def x(self) -> float | int:
        return self._x
    
    @x.setter
    def x(self, value: float | int):
        self._x = value

    @property
    def y(self) -> float | int:
        return self._y
    
    @y.setter
    def y(self, value: float | int):
        self._y = value

    @property
    def top(self) -> float | int:
        return self.y
    
    @top.setter
    def top(self, value: float | int):
        self.y = value
    
    @property
    def left(self) -> float | int:
        return self.x
    
    @left.setter
    def left(self, value: float | int):
        self.x = value

    @property
    def rngRadius(self) -> float | int:
        return self._rngRadius
    
    @rngRadius.setter
    def rngRadius(self, value: float | int):
        self._rngRadius = value
# endregion

    def randomPoint(self, rngRadius: float | int | None = None) -> iPoint:
        if 0 < self._x < 1.0 or 0 < self._y < 1.0 or 0 < self._rngRadius < 1.0:
            raise ValueError("Normalize the point before using randomPoint")

        rngRadius = self._rngRadius if rngRadius is None or rngRadius <= 0 else rngRadius
        x = random.uniform(self._x - rngRadius, self._x + rngRadius)
        y = random.uniform(self._y - rngRadius, self._y + rngRadius)
        return Point(x, y)

    def normalize(self, resolution: iPoint):
        if self._x >= 1.0: self._x = self._x / resolution.x
        if self._y >= 1.0: self._y = self._y / resolution.y
        if self._rngRadius >= 1.0: self._rngRadius = self._rngRadius / min(resolution.x, resolution.y)

    def scale(self, resolution: iPoint):
        if 0 < self._x < 1.0: self._x = self._x * resolution.x
        if 0 < self._y < 1.0: self._y = self._y * resolution.y
        if 0 < self._rngRadius < 1.0: self._rngRadius = self._rngRadius * min(resolution.x, resolution.y)
    
    def __str__(self) -> str:
        return f"{self.x}x{self.y}"