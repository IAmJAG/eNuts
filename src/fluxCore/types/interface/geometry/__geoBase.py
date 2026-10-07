# ==================================================================================
# src/fluxCore/contracts/geometry/__geoBase.py
# ==================================================================================
from typing import Protocol

# ==================================================================================
from .__point import iPoint


# ==================================================================================
class iGeometry(Protocol): 
    def randomPoint(self) -> iPoint: ...
    def normalize(self, resolution: iPoint): ...
    def scale(self, resolution: iPoint): ...
    @property
    def x(self) -> float | int: ...    
    @property
    def y(self) -> float | int: ...
    