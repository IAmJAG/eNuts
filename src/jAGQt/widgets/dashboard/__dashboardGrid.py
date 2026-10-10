# ==================================================================================
# src/jAGQt/widgets/dashboard/__dashboardGrid.py
# ==================================================================================
from __future__ import annotations

from typing import Optional, Tuple

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QSizePolicy, QWidget

# ==================================================================================
from jAGQt.types.interface.widgets.dashboard import iCard, iCardPlacement

# ==================================================================================
from ..components import ComponentBase
from .__cardPlacement import CardPlacement
from .__dragController import DragController
from .__gridModel import GridModel
from .__layoutResolver import LayoutResolver
from .__options import dashboardConfig
from .__resizeController import ResizeController


# ==================================================================================
class DashboardGrid(QWidget, ComponentBase):
    """Host: model → geometry; drag float + move-push; resize grow-push."""

    OBJECT_NAME = "DashboardGrid"

    def __init__(
        self,
        config: Optional[dashboardConfig] = None,
        parent: Optional[QWidget] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)
        self._config: dashboardConfig = (
            config if config is not None else dashboardConfig()
        )
        self._model: GridModel = GridModel(self._config)
        self._margins: int = self._config.margins
        self._resolver: LayoutResolver = LayoutResolver()
        self._drag: DragController = DragController(self)
        self._resize: ResizeController = ResizeController(self)

        self.setObjectName(self.OBJECT_NAME)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        self._drag.Attach(self)
        self._resize.Attach(self)

    # ==================================================================================
    @property
    def Model(self) -> GridModel:
        return self._model

    @property
    def Resolver(self) -> LayoutResolver:
        return self._resolver

    @property
    def IsDragging(self) -> bool:
        return self._drag.IsDragging

    @property
    def IsResizing(self) -> bool:
        return self._resize.IsResizing

    def HitResizeEdge(self, widget: QWidget, event: QMouseEvent) -> bool:
        return self._resize.HitEdge(widget, event) != 0

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

        if isinstance(card, QWidget):
            card.setParent(self)
            card.show()

        self._drag.OnCardAdded(card)
        self._resize.OnCardAdded(card)
        self.ApplyLayout()
        return lPlacement

    def RemoveCard(self, card: iCard) -> bool:
        self._drag.OnCardRemoved(card)
        self._resize.OnCardRemoved(card)
        lOk = self._model.RemoveByCard(card)
        if lOk and isinstance(card, QWidget):
            card.hide()
            card.setParent(None)
        self.ApplyLayout()
        return lOk

    def Clear(self) -> None:
        for lP in list(self._model.Placements):
            lCard = lP.Card
            self._drag.OnCardRemoved(lCard)
            self._resize.OnCardRemoved(lCard)
            if isinstance(lCard, QWidget):
                lCard.hide()
                lCard.setParent(None)
        self._model.Clear()
        self.ApplyLayout()

    def TryMove(
        self,
        card: iCard,
        col: int,
        row: int,
        floatCard: bool = False,
    ) -> bool:
        lP = self._model.GetPlacement(card)
        if lP is None:
            return False
        lChanged = self._resolver.ResolveMove(self._model, lP, int(col), int(row))
        if lChanged is None:
            return False
        self._model.Occupancy.Rebuild(self._model.Placements, self._model.Columns)
        self.ApplyLayout(skipCard=card if floatCard else None)
        return True

    def TryResize(self, card: iCard, colSpan: int, rowSpan: int) -> bool:
        lP = self._model.GetPlacement(card)
        if lP is None:
            return False
        lColSpan = max(card.MinColSpan, int(colSpan))
        lRowSpan = max(card.MinRowSpan, int(rowSpan))
        if lColSpan + lP.Col > self._model.Columns:
            return False

        if lColSpan < lP.ColSpan or lRowSpan < lP.RowSpan:
            # pure shrink (or mixed shrink on one axis) — self only for the
            # reduced axes; if the other axis grew, use grow path
            if lColSpan <= lP.ColSpan and lRowSpan <= lP.RowSpan:
                lChanged = self._resolver.ResolveShrink(
                    self._model, lP, lColSpan, lRowSpan
                )
                if lChanged is None:
                    return False
            else:
                lChanged = self._resolver.ResolveGrow(
                    self._model, lP, lColSpan, lRowSpan
                )
                if lChanged is None:
                    return False
        else:
            lChanged = self._resolver.ResolveGrow(
                self._model, lP, lColSpan, lRowSpan
            )
            if lChanged is None:
                return False

        self._model.Occupancy.Rebuild(self._model.Placements, self._model.Columns)
        self.ApplyLayout()
        return True

    def CellAt(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        lMargin = self._margins
        lGap = self._model.Gap
        lCols = self._model.Columns
        lRows = max(1, self._model.RowCount())
        lW = max(0, self.width())
        lH = max(0, self.height())

        lInnerW = max(0, lW - 2 * lMargin - lGap * (lCols - 1))
        lCellW = lInnerW // lCols if lCols else 0
        lInnerH = max(0, lH - 2 * lMargin - lGap * (lRows - 1))
        lMinCellH = self._model.CellMinHeight
        lCellH = max(lMinCellH, lInnerH // lRows if lRows else lMinCellH)

        if lCellW <= 0 or lCellH <= 0:
            return (0, 0)

        lCol = (int(x) - lMargin) // (lCellW + lGap)
        lRow = (int(y) - lMargin) // (lCellH + lGap)
        lCol = max(0, min(lCols - 1, lCol))
        lRow = max(0, lRow)
        return (lCol, lRow)

    def ApplyLayout(self, skipCard: Optional[iCard] = None) -> None:
        lSkip = skipCard
        if lSkip is None and self._drag.IsDragging:
            lSkip = self._drag.CurrentCard

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
            if lSkip is not None and lCard is lSkip:
                lCard.raise_()
                continue
            lX = lMargin + lP.Col * (lCellW + lGap)
            lY = lMargin + lP.Row * (lCellH + lGap)
            lCw = lP.ColSpan * lCellW + (lP.ColSpan - 1) * lGap
            lCh = lP.RowSpan * lCellH + (lP.RowSpan - 1) * lGap
            lCard.setGeometry(lX, lY, max(0, lCw), max(0, lCh))
            lCard.show()
            lCard.raise_()

        if lSkip is not None and isinstance(lSkip, QWidget):
            lSkip.raise_()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.ApplyLayout()
