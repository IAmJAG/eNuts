# ==================================================================================
# src/jAGQt/types/interface/widgets/dashboard/__occupancyMap.py
# ==================================================================================
from typing import List, Optional, Protocol, Sequence, Tuple, runtime_checkable

# ==================================================================================
from .__cardPlacement import iCardPlacement


# ==================================================================================
@runtime_checkable
class iOccupancyMap(Protocol):
    """Cell occupancy queries over a set of placements."""

    def Rebuild(self, placements: Sequence[iCardPlacement], columns: int) -> None: ...

    def IsCellFree(self, col: int, row: int) -> bool: ...

    def IsRegionFree(
        self, col: int, row: int, colSpan: int, rowSpan: int,
        ignore: Optional[iCardPlacement] = None,
    ) -> bool: ...

    def GetOverlaps(
        self, col: int, row: int, colSpan: int, rowSpan: int,
        ignore: Optional[iCardPlacement] = None,
    ) -> List[iCardPlacement]: ...

    def FindNearestFree(
        self,
        colSpan: int,
        rowSpan: int,
        fromCol: int = 0,
        fromRow: int = 0,
        maxRow: int = 64,
    ) -> Optional[Tuple[int, int]]: ...
