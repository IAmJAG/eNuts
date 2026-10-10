# ==================================================================================
# src/jAGQt/widgets/dashboard/__gridModel.py
# ==================================================================================
from __future__ import annotations

from typing import Dict, List, Optional
from uuid import UUID

# ==================================================================================
from jAGQt.types.interface.widgets.dashboard import iCard, iCardPlacement

# ==================================================================================
from .__occupancyMap import OccupancyMap
from .__options import dashboardConfig


# ==================================================================================
class GridModel:
    """Placement source of truth + occupancy helper."""

    def __init__(self, config: Optional[dashboardConfig] = None) -> None:
        lCfg = config if config is not None else dashboardConfig()
        self._columns: int = max(1, lCfg.columns)
        self._gap: int = max(0, lCfg.gap)
        self._cellMinHeight: int = max(1, lCfg.cellMinHeight)
        self._placements: List[iCardPlacement] = []
        self._byCardId: Dict[str, iCardPlacement] = {}
        self._occupancy: OccupancyMap = OccupancyMap()

    def _rebuildOccupancy(self) -> None:
        self._occupancy.Rebuild(self._placements, self._columns)

    def _cardKey(self, card: iCard) -> str:
        return str(card.Id)

    @property
    def Columns(self) -> int:
        return self._columns

    @Columns.setter
    def Columns(self, value: int) -> None:
        self._columns = max(1, int(value))
        self._rebuildOccupancy()

    @property
    def Gap(self) -> int:
        return self._gap

    @property
    def CellMinHeight(self) -> int:
        return self._cellMinHeight

    @property
    def Placements(self) -> List[iCardPlacement]:
        return list(self._placements)

    @property
    def Occupancy(self) -> OccupancyMap:
        return self._occupancy

    def AddPlacement(self, placement: iCardPlacement) -> bool:
        lKey = self._cardKey(placement.Card)
        if lKey in self._byCardId:
            return False
        if placement.Col + placement.ColSpan > self._columns:
            return False
        if not self._occupancy.IsRegionFree(
            placement.Col, placement.Row, placement.ColSpan, placement.RowSpan
        ):
            return False
        self._placements.append(placement)
        self._byCardId[lKey] = placement
        self._rebuildOccupancy()
        return True

    def RemoveByCard(self, card: iCard) -> bool:
        lKey = self._cardKey(card)
        lP = self._byCardId.pop(lKey, None)
        if lP is None:
            return False
        self._placements = [p for p in self._placements if p is not lP]
        self._rebuildOccupancy()
        return True

    def GetPlacement(self, card: iCard) -> Optional[iCardPlacement]:
        return self._byCardId.get(self._cardKey(card))

    def Clear(self) -> None:
        self._placements.clear()
        self._byCardId.clear()
        self._rebuildOccupancy()

    def ExportLayout(self) -> List[Dict[str, int | str]]:
        lOut: List[Dict[str, int | str]] = []
        for lP in self._placements:
            lOut.append(
                {
                    "id": str(lP.Card.Id),
                    "col": lP.Col,
                    "row": lP.Row,
                    "colSpan": lP.ColSpan,
                    "rowSpan": lP.RowSpan,
                }
            )
        return lOut

    def RowCount(self) -> int:
        if not self._placements:
            return 1
        return max(p.Row + p.RowSpan for p in self._placements)

    def FindAutoSlot(self, colSpan: int, rowSpan: int) -> Optional[tuple[int, int]]:
        self._rebuildOccupancy()
        return self._occupancy.FindNearestFree(colSpan, rowSpan)
