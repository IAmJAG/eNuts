# ==================================================================================
# src/jAGQt/widgets/dashboard/__occupancyMap.py
# ==================================================================================
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

# ==================================================================================
from jAGQt.types.interface.widgets.dashboard import iCardPlacement


# ==================================================================================
class OccupancyMap:
    """Cell occupancy built from placements."""

    def __init__(self) -> None:
        self._columns: int = 4
        self._cells: Dict[Tuple[int, int], iCardPlacement] = {}
        self._placements: List[iCardPlacement] = []

    def Rebuild(self, placements: Sequence[iCardPlacement], columns: int) -> None:
        self._columns = max(1, int(columns))
        self._cells.clear()
        self._placements = list(placements)
        for lP in self._placements:
            lC, lR, lW, lH = lP.Rect()
            for lDy in range(lH):
                for lDx in range(lW):
                    self._cells[(lC + lDx, lR + lDy)] = lP

    def IsCellFree(self, col: int, row: int) -> bool:
        if col < 0 or row < 0 or col >= self._columns:
            return False
        return (col, row) not in self._cells

    def IsRegionFree(
        self,
        col: int,
        row: int,
        colSpan: int,
        rowSpan: int,
        ignore: Optional[iCardPlacement] = None,
    ) -> bool:
        if col < 0 or row < 0 or colSpan < 1 or rowSpan < 1:
            return False
        if col + colSpan > self._columns:
            return False
        for lDy in range(rowSpan):
            for lDx in range(colSpan):
                lOcc = self._cells.get((col + lDx, row + lDy))
                if lOcc is not None and lOcc is not ignore:
                    return False
        return True

    def GetOverlaps(
        self,
        col: int,
        row: int,
        colSpan: int,
        rowSpan: int,
        ignore: Optional[iCardPlacement] = None,
    ) -> List[iCardPlacement]:
        lSeen: set[int] = set()
        lOut: List[iCardPlacement] = []
        for lDy in range(max(0, rowSpan)):
            for lDx in range(max(0, colSpan)):
                lOcc = self._cells.get((col + lDx, row + lDy))
                if lOcc is None or lOcc is ignore:
                    continue
                lKey = id(lOcc)
                if lKey in lSeen:
                    continue
                lSeen.add(lKey)
                lOut.append(lOcc)
        return lOut

    def FindNearestFree(
        self,
        colSpan: int,
        rowSpan: int,
        fromCol: int = 0,
        fromRow: int = 0,
        maxRow: int = 64,
    ) -> Optional[Tuple[int, int]]:
        lColSpan = max(1, int(colSpan))
        lRowSpan = max(1, int(rowSpan))
        if lColSpan > self._columns:
            return None
        for lRow in range(max(0, fromRow), maxRow):
            for lCol in range(0, self._columns - lColSpan + 1):
                if self.IsRegionFree(lCol, lRow, lColSpan, lRowSpan):
                    return (lCol, lRow)
        return None
