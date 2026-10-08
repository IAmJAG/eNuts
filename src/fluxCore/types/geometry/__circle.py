# ==================================================================================
# src/fluxCore/geometry/__circle.py
# ==================================================================================
import math
import random

# ==================================================================================
from jAGFx.serializer import Serializable

# ==================================================================================
from ..interface.geometry import iGeometry, iPoint
from .__point import Point


# ==================================================================================
class Circle(Serializable, iGeometry):
    def __init__(self, x: float | int, y: float | int, radius: float | int = 5.0):
        super().__init__()
        self._x: float | int = x
        self._y: float | int = y
        self._radius: float | int = radius
        self.Properties.extend(["x", "y", "radius"])

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
    def radius(self) -> float | int:
        return self._radius
    
    @radius.setter
    def radius(self, value: float | int):
        self._radius = value

    @property
    def center(self) -> iPoint:
        return Point(self.x, self.y)

    def randomPoint(self) -> iPoint:
        if 0 < self._x < 1.0 or 0 < self._y < 1.0 or 0 < self._radius < 1.0:
            raise ValueError("Normalize the circle before using randomPoint")
        
        theta = random.uniform(0, 2 * math.pi)
        x = int(self._x + self._radius * math.cos(theta))
        y = int(self._y + self._radius * math.sin(theta))
        return Point(x, y)

    def normalize(self, resolution: iPoint):
        if self._x >= 1.0: self._x = self._x / resolution.x
        if self._y >= 1.0: self._y = self._y / resolution.y
        if self._radius >= 1.0: self._radius = self._radius / min(resolution.x, resolution.y)
    
    def scale(self, resolution: iPoint):
        if 0 < self._x < 1.0: self._x = self._x * resolution.x
        if 0 < self._y < 1.0: self._y = self._y * resolution.y
        if 0 < self._radius < 1.0: self._radius = self._radius * min(resolution.x, resolution.y)

    def __str__(self) -> str:
        return f"{self._x}x{self._y}x{self._radius}"