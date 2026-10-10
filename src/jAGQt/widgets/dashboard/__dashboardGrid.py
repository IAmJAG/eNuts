# ==================================================================================
# src/jAGQt/widgets/dashboard/__dashboardGrid.py
# ==================================================================================
from __future__ import annotations

from typing import Optional

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSizePolicy, QWidget

# ==================================================================================
from jAGQt.types.interface.widgets.dashboard import iCard, iCardPlacement

# ==================================================================================
from ..components import ComponentBase
from .__cardPlacement import CardPlacement
from .__gridModel import GridModel
from .__options import dashboardConfig


# ==================================================================================
class DashboardGrid(QWidget, ComponentBase):
    """Host: applies GridModel placements to card geometries (Phase 1 static)."""

    OBJECT_NAME = "DashboardGrid"

    def __init__(
        self,
        config: Optional[dashboardConfig] = None,
        parent: Optional[QWidget] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)
        self._config: dashboardConfig = config if config is not None else dashboardConfig()
        self._model: GridModel = GridModel(self._config)
        self._margins: int = self._config.margins

        self.setObjectName(self.OBJECT_NAME)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

    # ==================================================================================
    @property
    def Model(self) -> GridModel:
        return self._model

    def AddCard(
        self,
        card: iCard,
        col: Optional[int] = None,
        row: Optional[int] = None,
        colSpan: Optional[int] = None,
        rowSpan: Optional[int] = None,
    ) -> Optional[iCardPlacement]:
        lColSpan = colSpan if colSpan is not None else card.PreferredColSpan
        lRowSpan = rowSpan if rowSpan is not None else card.PreferredRowSpan
        lColSpan = max(card.MinColSpan, int(lColSpan))
        lRowSpan = max(card.MinRowSpan, int(lRowSpan))

        if col is None or row is None:
            lSlot = self._model.FindAutoSlot(lColSpan, lRowSpan)
            if lSlot is None:
                return None
            lCol, lRow = lSlot
            if col is not None:
                lCol = col
            if row is not None:
                lRow = row
        else:
            lCol, lRow = int(col), int(row)

        lPlacement = CardPlacement(card, lCol, lRow, lColSpan, lRowSpan)
        if not self._model.AddPlacement(lPlacement):
            return None

        # Card is a QWidget in practice; parent under the grid host
        if isinstance(card, QWidget):
            card.setParent(self)
            card.show()

        self.ApplyLayout()
        return lPlacement

    def RemoveCard(self, card: iCard) -> bool:
        lOk = self._model.RemoveByCard(card)
        if lOk and isinstance(card, QWidget):
            card.hide()
            card.setParent(None)
        self.ApplyLayout()
        return lOk

    def Clear(self) -> None:
        for lP in list(self._model.Placements):
            lCard = lP.Card
            if isinstance(lCard, QWidget):
                lCard.hide()
                lCard.setParent(None)
        self._model.Clear()
        self.ApplyLayout()

    def TryMove(self, card: iCard, col: int, row: int) -> bool:
        """Phase 1: relocate only if target region is free (no push yet)."""
        lP = self._model.GetPlacement(card)
        if lP is None:
            return False
        lOcc = self._model.Occupancy
        lOcc.Rebuild(self._model.Placements, self._model.Columns)
        if not lOcc.IsRegionFree(col, row, lP.ColSpan, lP.RowSpan, ignore=lP):
            return False
        lP.Col = col
        lP.Row = row
        self._model.Occupancy.Rebuild(self._model.Placements, self._model.Columns)
        self.ApplyLayout()
        return True

    def TryResize(self, card: iCard, colSpan: int, rowSpan: int) -> bool:
        """Phase 1: resize only if expanded region is free; shrink always ok."""
        lP = self._model.GetPlacement(card)
        if lP is None:
            return False
        lColSpan = max(card.MinColSpan, int(colSpan))
        lRowSpan = max(card.MinRowSpan, int(rowSpan))
        if lColSpan + lP.Col > self._model.Columns:
            return False
        if lColSpan >= lP.ColSpan and lRowSpan >= lP.RowSpan:
            lOcc = self._model.Occupancy
            lOcc.Rebuild(self._model.Placements, self._model.Columns)
            if not lOcc.IsRegionFree(
                lP.Col, lP.Row, lColSpan, lRowSpan, ignore=lP
            ):
                return False
        lP.ColSpan = lColSpan
        lP.RowSpan = lRowSpan
        self._model.Occupancy.Rebuild(self._model.Placements, self._model.Columns)
        self.ApplyLayout()
        return True

    def ApplyLayout(self) -> None:
        lW = max(0, self.width())
        lH = max(0, self.height())
        lMargin = self._margins
        lGap = self._model.Gap
        lCols = self._model.Columns
        lRows = max(1, self._model.RowCount())

        lInnerW = max(0, lW - 2 * lMargin - lGap * (lCols - 1))
        lCellW = lInnerW // lCols if lCols else 0

        lInnerH = max(0, lH - 2 * lMargin - lGap * (lRows - 1))
        lMinCellH = self._model.CellMinHeight
        lCellH = max(lMinCellH, lInnerH // lRows if lRows else lMinCellH)

        for lP in self._model.Placements:
            lCard = lP.Card
            if not isinstance(lCard, QWidget):
                continue
            lX = lMargin + lP.Col * (lCellW + lGap)
            lY = lMargin + lP.Row * (lCellH + lGap)
            lCw = lP.ColSpan * lCellW + (lP.ColSpan - 1) * lGap
            lCh = lP.RowSpan * lCellH + (lP.RowSpan - 1) * lGap
            lCard.setGeometry(lX, lY, max(0, lCw), max(0, lCh))
            lCard.show()
            lCard.raise_()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.ApplyLayout()
