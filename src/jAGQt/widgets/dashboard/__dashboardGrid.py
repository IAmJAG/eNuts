# ==================================================================================
# src/jAGQt/widgets/dashboard/__dashboardGrid.py
# ==================================================================================
from __future__ import annotations

from typing import Optional, Tuple

# ==================================================================================
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QMouseEvent, QShowEvent
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
    """Host: fixed 64px cell units; fills parent content area; drag/resize."""

    OBJECT_NAME = "DashboardGrid"

    # TEMP: visible host bounds — remove once layout verified
    _C_DEBUG_EDGE = True

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
        self.setMinimumSize(0, 0)

        if self._C_DEBUG_EDGE:
            # Temporary: cyan border + tint so host bounds are obvious
            self.setStyleSheet(
                "#DashboardGrid {"
                "  background-color: rgba(0, 180, 255, 35);"
                "  border: 2px solid #00b4ff;"
                "}"
            )

        self._drag.Attach(self)
        self._resize.Attach(self)

    # ==================================================================================
    def sizeHint(self) -> QSize:
        lMargin = self._margins
        lGap = self._model.Gap
        lCell = self._model.CellSize
        lCols = self._model.Columns
        lRows = max(1, self._model.RowCount())
        lW = 2 * lMargin + lCols * lCell + max(0, lCols - 1) * lGap
        lH = 2 * lMargin + lRows * lCell + max(0, lRows - 1) * lGap
        return QSize(lW, lH)

    def minimumSizeHint(self) -> QSize:
        return QSize(0, 0)

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
            card.hide()

        self._drag.OnCardAdded(card)
        self._resize.OnCardAdded(card)
        self.ApplyLayout()
        self.updateGeometry()
        return lPlacement

    def RemoveCard(self, card: iCard) -> bool:
        self._drag.OnCardRemoved(card)
        self._resize.OnCardRemoved(card)
        lOk = self._model.RemoveByCard(card)
        if lOk and isinstance(card, QWidget):
            card.hide()
            card.setParent(None)
        self.ApplyLayout()
        self.updateGeometry()
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
        self.updateGeometry()

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

        if lColSpan <= lP.ColSpan and lRowSpan <= lP.RowSpan:
            lChanged = self._resolver.ResolveShrink(
                self._model, lP, lColSpan, lRowSpan
            )
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
        lCell = self._model.CellSize

        if lCell <= 0:
            return (0, 0)

        lStep = lCell + lGap
        lCol = (int(x) - lMargin) // lStep
        lRow = (int(y) - lMargin) // lStep
        lCol = max(0, min(lCols - 1, lCol))
        lRow = max(0, lRow)
        return (lCol, lRow)

    def ApplyLayout(self, skipCard: Optional[iCard] = None) -> None:
        lSkip = skipCard
        if lSkip is None and self._drag.IsDragging:
            lSkip = self._drag.CurrentCard

        lMargin = self._margins
        lGap = self._model.Gap
        lCell = self._model.CellSize
        lReveal = self.isVisible()

        for lP in self._model.Placements:
            lCard = lP.Card
            if not isinstance(lCard, QWidget):
                continue
            if lSkip is not None and lCard is lSkip:
                lCard.raise_()
                continue
            lX = lMargin + lP.Col * (lCell + lGap)
            lY = lMargin + lP.Row * (lCell + lGap)
            lCw = lP.ColSpan * lCell + (lP.ColSpan - 1) * lGap
            lCh = lP.RowSpan * lCell + (lP.RowSpan - 1) * lGap
            lCard.setGeometry(lX, lY, max(0, lCw), max(0, lCh))
            if lReveal:
                lCard.show()
            else:
                lCard.hide()
            lCard.raise_()

        if lSkip is not None and isinstance(lSkip, QWidget):
            lSkip.raise_()

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self.ApplyLayout()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.ApplyLayout()
