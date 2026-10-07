# ==================================================================================
# src/fluxCore/actions/shapes/__rectangle.py
# ==================================================================================
import random

# ==================================================================================
from typing import runtime_checkable

# ==================================================================================
from jAGFx.serializer import Serializeable

# ==================================================================================
from ..contracts.geometry.__point import iPoint
from .__point import Point


# ==================================================================================
class Rectangle(Serializeable):
    def __init__(self, x: float, y: float, width: float, height: float):
        super().__init__()
        self._x: float | int = float(x)
        self._y: float | int = float(y)
        self._width: float | int = float(width) 
        self._height: float | int = float(height)
        self.Properties.extend(["x", "y", "width", "height"])

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
    def width(self) -> float | int:
        return self._width

    @width.setter
    def width(self, value: float | int):
        self._width = value

    @property
    def height(self) -> float | int:
        return self._height

    @height.setter
    def height(self, value: float | int):
        self._height = value

    @property
    def top(self) -> float | int:
        return self.y
    
    @property
    def left(self) -> float | int:
        return self.x

    @property
    def right(self) -> float | int:
        return self.x + self.width
    
    @property
    def bottom(self) -> float | int:
        return self.y + self.height
    
    @property
    def center(self) -> iPoint:
        return Point(self.x + self.width / 2, self.y + self.height / 2) 

    @property
    def topLeft(self) -> iPoint:
        return Point(self.x, self.y)
    
    @property
    def topRight(self) -> iPoint:
        return Point(self.x + self.width, self.y)
    
    @property
    def bottomLeft(self) -> iPoint:
        return Point(self.x, self.y + self.height)
    
    @property
    def bottomRight(self) -> iPoint:
        return Point(self.x + self.width, self.y + self.height)
    
    def randomPoint(self) -> iPoint:
        if 0 < self._width < 1.0 or 0 < self._height < 1.0 or 0 < self._x < 1.0 or 0 < self._y < 1.0:
            raise ValueError("Normalize the rectangle before using randomPoint")
        
        x = int(random.uniform(self._x, self._x + self._width))
        y = int(random.uniform(self._y, self._y + self._height))
        return Point(x, y)
    
    def normalize(self, resolution: iPoint):
        if self._x >= 1.0: self._x = self._x / resolution.x
        if self._y >= 1.0: self._y = self._y / resolution.y
        if self._width >= 1.0: self._width = self._width / resolution.x
        if self._height >= 1.0: self._height = self._height / resolution.y

    def scale(self, resolution: iPoint):
        if 0 < self._x < 1.0: self._x = self._x * resolution.x
        if 0 < self._y < 1.0: self._y = self._y * resolution.y
        if 0 < self._width < 1.0: self._width = self._width * resolution.x
        if 0 < self._height < 1.0: self._height = self._height * resolution.y

    def __str__(self) -> str:
        return f"{self.x}x{self.y}x{self.width}x{self.height}"