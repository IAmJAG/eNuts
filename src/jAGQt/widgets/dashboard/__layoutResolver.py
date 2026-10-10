# ==================================================================================
# src/jAGQt/widgets/dashboard/__layoutResolver.py
# ==================================================================================
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

# ==================================================================================
from jAGQt.types.interface.widgets.dashboard import (
    iCardPlacement,
    iGridModel,
)

# ==================================================================================
from .__occupancyMap import OccupancyMap


# ==================================================================================
class _WorkingPlacement:
    """Mutable snapshot of a placement for resolution passes."""

    def __init__(self, source: iCardPlacement) -> None:
        self.Source: iCardPlacement = source
        self.Col: int = source.Col
        self.Row: int = source.Row
        self.ColSpan: int = source.ColSpan
        self.RowSpan: int = source.RowSpan

    def Rect(self) -> Tuple[int, int, int, int]:
        return (self.Col, self.Row, self.ColSpan, self.RowSpan)


# ==================================================================================
class LayoutResolver:
    """Collision resolution. Move pushes blockers to free cells of equal size."""

    def __init__(self, maxRowSearch: int = 64) -> None:
        self._maxRowSearch: int = max(8, int(maxRowSearch))

    # ----------------------------------------------------------------------------------
    def ResolveMove(
        self,
        model: iGridModel,
        placement: iCardPlacement,
        newCol: int,
        newRow: int,
    ) -> Optional[List[iCardPlacement]]:
        lColumns = model.Columns
        if newCol < 0 or newRow < 0:
            return None
        if newCol + placement.ColSpan > lColumns:
            return None
        if newCol == placement.Col and newRow == placement.Row:
            return [placement]

        lWork: Dict[int, _WorkingPlacement] = {}
        for lP in model.Placements:
            lWork[id(lP)] = _WorkingPlacement(lP)

        lMoverKey = id(placement)
        if lMoverKey not in lWork:
            return None
        lMover = lWork[lMoverKey]
        lMover.Col = newCol
        lMover.Row = newRow

        lOcc = self._buildOcc(lWork, lColumns)
        lOverlaps = lOcc.GetOverlaps(
            newCol, newRow, placement.ColSpan, placement.RowSpan, ignore=None
        )
        # GetOverlaps uses placement identity in cells — rebuild with working refs
        lBlockers = self._overlapsFromWork(
            lWork, lMoverKey, newCol, newRow, placement.ColSpan, placement.RowSpan
        )

        for lBlocker in lBlockers:
            lSlot = self._findFreeFor(
                lWork,
                lColumns,
                lBlocker,
                preferCol=newCol,
                preferRow=newRow,
                excludeKeys={lMoverKey, id(lBlocker.Source)},
            )
            if lSlot is None:
                return None
            lBlocker.Col, lBlocker.Row = lSlot

        # Final conflict check among all working positions
        if not self._isConsistent(lWork, lColumns):
            return None

        lChanged: List[iCardPlacement] = []
        for lW in lWork.values():
            lSrc = lW.Source
            if (
                lSrc.Col != lW.Col
                or lSrc.Row != lW.Row
                or lSrc.ColSpan != lW.ColSpan
                or lSrc.RowSpan != lW.RowSpan
            ):
                lSrc.Col = lW.Col
                lSrc.Row = lW.Row
                lSrc.ColSpan = lW.ColSpan
                lSrc.RowSpan = lW.RowSpan
                lChanged.append(lSrc)

        return lChanged if lChanged else [placement]

    def ResolveGrow(
        self,
        model: iGridModel,
        placement: iCardPlacement,
        newColSpan: int,
        newRowSpan: int,
    ) -> Optional[List[iCardPlacement]]:
        """Phase 3 — reserved."""
        return None

    def ResolveShrink(
        self,
        model: iGridModel,
        placement: iCardPlacement,
        newColSpan: int,
        newRowSpan: int,
    ) -> Optional[List[iCardPlacement]]:
        lColSpan = max(placement.Card.MinColSpan, int(newColSpan))
        lRowSpan = max(placement.Card.MinRowSpan, int(newRowSpan))
        if lColSpan > placement.ColSpan or lRowSpan > placement.RowSpan:
            return None
        placement.ColSpan = lColSpan
        placement.RowSpan = lRowSpan
        return [placement]

    # ----------------------------------------------------------------------------------
    def _buildOcc(
        self, work: Dict[int, _WorkingPlacement], columns: int
    ) -> OccupancyMap:
        # OccupancyMap expects iCardPlacement; use Sources with temp coords via a shim list
        # We only need geometry checks on work dict — use dedicated helpers instead.
        return OccupancyMap()

    def _overlapsFromWork(
        self,
        work: Dict[int, _WorkingPlacement],
        moverKey: int,
        col: int,
        row: int,
        colSpan: int,
        rowSpan: int,
    ) -> List[_WorkingPlacement]:
        lOut: List[_WorkingPlacement] = []
        lSeen: set[int] = set()
        for lKey, lW in work.items():
            if lKey == moverKey:
                continue
            if self._rectsOverlap(
                col, row, colSpan, rowSpan, lW.Col, lW.Row, lW.ColSpan, lW.RowSpan
            ):
                if lKey not in lSeen:
                    lSeen.add(lKey)
                    lOut.append(lW)
        return lOut

    def _rectsOverlap(
        self,
        c0: int, r0: int, w0: int, h0: int,
        c1: int, r1: int, w1: int, h1: int,
    ) -> bool:
        return not (c0 + w0 <= c1 or c1 + w1 <= c0 or r0 + h0 <= r1 or r1 + h1 <= r0)

    def _findFreeFor(
        self,
        work: Dict[int, _WorkingPlacement],
        columns: int,
        blocker: _WorkingPlacement,
        preferCol: int,
        preferRow: int,
        excludeKeys: set[int],
    ) -> Optional[Tuple[int, int]]:
        lW = blocker.ColSpan
        lH = blocker.RowSpan
        if lW > columns:
            return None

        def regionFree(col: int, row: int) -> bool:
            if col < 0 or row < 0 or col + lW > columns:
                return False
            for lKey, lOther in work.items():
                if lKey in excludeKeys:
                    continue
                if self._rectsOverlap(
                    col, row, lW, lH,
                    lOther.Col, lOther.Row, lOther.ColSpan, lOther.RowSpan,
                ):
                    return False
            return True

        # Prefer slots near the intrusion, scan outward by row then col
        lCandidates: List[Tuple[int, int, int]] = []
        for lRow in range(0, self._maxRowSearch):
            for lCol in range(0, columns - lW + 1):
                if regionFree(lCol, lRow):
                    lDist = abs(lCol - preferCol) + abs(lRow - preferRow)
                    lCandidates.append((lDist, lCol, lRow))
        if not lCandidates:
            return None
        lCandidates.sort()
        return (lCandidates[0][1], lCandidates[0][2])

    def _isConsistent(
        self, work: Dict[int, _WorkingPlacement], columns: int
    ) -> bool:
        lItems = list(work.values())
        for lI, lA in enumerate(lItems):
            if lA.Col < 0 or lA.Row < 0 or lA.Col + lA.ColSpan > columns:
                return False
            for lB in lItems[lI + 1 :]:
                if self._rectsOverlap(
                    lA.Col, lA.Row, lA.ColSpan, lA.RowSpan,
                    lB.Col, lB.Row, lB.ColSpan, lB.RowSpan,
                ):
                    return False
        return True
