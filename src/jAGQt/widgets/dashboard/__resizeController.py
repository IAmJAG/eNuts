# ==================================================================================
# src/jAGQt/widgets/dashboard/__resizeController.py
# ==================================================================================
from __future__ import annotations

from typing import Optional, TYPE_CHECKING

# ==================================================================================
from PySide6.QtCore import QEvent, QObject, QPoint, Qt
from PySide6.QtGui import QCursor, QMouseEvent
from PySide6.QtWidgets import QWidget

# ==================================================================================
from jAGQt.types.interface.widgets.dashboard import iCard

# ==================================================================================
if TYPE_CHECKING:
    from .__dashboardGrid import DashboardGrid

# ==================================================================================
_C_EDGE = 8  # px hit zone

# edge flags
_C_L = 1
_C_R = 2
_C_T = 4
_C_B = 8


# ==================================================================================
class ResizeController(QObject):
    """Edge/corner resize. Grow may shrink others; shrink is self-only."""

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._grid: Optional["DashboardGrid"] = None
        self._resizing: bool = False
        self._card: Optional[iCard] = None
        self._edges: int = 0
        self._originCol: int = 0
        self._originRow: int = 0
        self._originColSpan: int = 1
        self._originRowSpan: int = 1
        self._pressGlobal: QPoint = QPoint()

    def Attach(self, grid: "DashboardGrid") -> None:
        self.Detach()
        self._grid = grid
        for lP in grid.Model.Placements:
            self.OnCardAdded(lP.Card)

    def Detach(self) -> None:
        if self._grid is not None:
            for lP in self._grid.Model.Placements:
                self.OnCardRemoved(lP.Card)
        self._grid = None
        self._endResize()

    def OnCardAdded(self, card: iCard) -> None:
        if isinstance(card, QWidget):
            card.installEventFilter(self)
            card.setMouseTracking(True)

    def OnCardRemoved(self, card: iCard) -> None:
        if isinstance(card, QWidget):
            card.removeEventFilter(self)

    @property
    def IsResizing(self) -> bool:
        return self._resizing

    @property
    def CurrentCard(self) -> Optional[iCard]:
        return self._card if self._resizing else None

    def HitEdge(self, widget: QWidget, event: QMouseEvent) -> int:
        lCard = self._cardFromWidget(widget)
        if lCard is None or not isinstance(lCard, QWidget):
            return 0
        lPos = lCard.mapFromGlobal(event.globalPosition().toPoint())
        return self._edgeAt(lCard, lPos)

    # ----------------------------------------------------------------------------------
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if self._grid is None:
            return False
        if getattr(self._grid, "IsDragging", False):
            return False

        lType = event.type()
        if lType == QEvent.Type.MouseButtonPress:
            return self._onPress(watched, event)  # type: ignore[arg-type]
        if lType == QEvent.Type.MouseMove:
            return self._onMove(watched, event)  # type: ignore[arg-type]
        if lType == QEvent.Type.MouseButtonRelease:
            return self._onRelease(watched, event)  # type: ignore[arg-type]
        return False

    def _onPress(self, watched: QObject, event: QMouseEvent) -> bool:
        if event.button() != Qt.MouseButton.LeftButton:
            return False
        if not isinstance(watched, QWidget):
            return False

        lCard = self._cardFromWidget(watched)
        if lCard is None or not isinstance(lCard, QWidget):
            return False

        lPos = lCard.mapFromGlobal(event.globalPosition().toPoint())
        lEdges = self._edgeAt(lCard, lPos)
        if lEdges == 0:
            return False

        lP = self._grid.Model.GetPlacement(lCard)  # type: ignore[union-attr]
        if lP is None:
            return False

        self._resizing = True
        self._card = lCard
        self._edges = lEdges
        self._originCol = lP.Col
        self._originRow = lP.Row
        self._originColSpan = lP.ColSpan
        self._originRowSpan = lP.RowSpan
        self._pressGlobal = event.globalPosition().toPoint()
        lCard.SetResizing(True)
        lCard.grabMouse()
        lCard.raise_()
        return True

    def _onMove(self, watched: QObject, event: QMouseEvent) -> bool:
        if not isinstance(watched, QWidget):
            return False

        if not self._resizing:
            # Hover cursor on edges
            lCard = self._cardFromWidget(watched)
            if lCard is not None and isinstance(lCard, QWidget):
                lPos = lCard.mapFromGlobal(event.globalPosition().toPoint())
                lEdges = self._edgeAt(lCard, lPos)
                lCard.setCursor(self._cursorFor(lEdges))
            return False

        if self._card is None or self._grid is None:
            return False

        lGlobal = event.globalPosition().toPoint()
        lInGrid = self._grid.mapFromGlobal(lGlobal)
        lCell = self._grid.CellAt(lInGrid.x(), lInGrid.y())
        if lCell is None:
            return True

        lCol, lRow = lCell
        lNewCol = self._originCol
        lNewRow = self._originRow
        lNewColSpan = self._originColSpan
        lNewRowSpan = self._originRowSpan

        if self._edges & _C_R:
            lNewColSpan = max(
                self._card.MinColSpan, lCol - self._originCol + 1
            )
        if self._edges & _C_B:
            lNewRowSpan = max(
                self._card.MinRowSpan, lRow - self._originRow + 1
            )
        if self._edges & _C_L:
            lRight = self._originCol + self._originColSpan
            lNewCol = min(lCol, lRight - self._card.MinColSpan)
            lNewCol = max(0, lNewCol)
            lNewColSpan = lRight - lNewCol
        if self._edges & _C_T:
            lBottom = self._originRow + self._originRowSpan
            lNewRow = min(lRow, lBottom - self._card.MinRowSpan)
            lNewRow = max(0, lNewRow)
            lNewRowSpan = lBottom - lNewRow

        lP = self._grid.Model.GetPlacement(self._card)
        if lP is None:
            return True

        # Apply position shift first when left/top edges move
        if lNewCol != lP.Col or lNewRow != lP.Row:
            self._grid.TryMove(self._card, lNewCol, lNewRow, floatCard=False)

        self._grid.TryResize(self._card, lNewColSpan, lNewRowSpan)
        return True

    def _onRelease(self, watched: QObject, event: QMouseEvent) -> bool:
        if not self._resizing:
            return False
        if event.button() != Qt.MouseButton.LeftButton:
            return False
        self._endResize()
        return True

    def _endResize(self) -> None:
        lCard = self._card
        self._resizing = False
        self._card = None
        self._edges = 0
        if lCard is not None and isinstance(lCard, QWidget):
            lCard.SetResizing(False)
            lCard.setCursor(Qt.CursorShape.OpenHandCursor)
            if QWidget.mouseGrabber() is lCard:
                lCard.releaseMouse()
        if self._grid is not None:
            self._grid.ApplyLayout()

    def _edgeAt(self, card: QWidget, pos: QPoint) -> int:
        lW = card.width()
        lH = card.height()
        lX = pos.x()
        lY = pos.y()
        if lX < 0 or lY < 0 or lX > lW or lY > lH:
            return 0
        lEdges = 0
        if lX <= _C_EDGE:
            lEdges |= _C_L
        if lX >= lW - _C_EDGE:
            lEdges |= _C_R
        if lY <= _C_EDGE:
            lEdges |= _C_T
        if lY >= lH - _C_EDGE:
            lEdges |= _C_B
        return lEdges

    def _cursorFor(self, edges: int) -> Qt.CursorShape:
        if edges == (_C_L | _C_T) or edges == (_C_R | _C_B):
            return Qt.CursorShape.SizeFDiagCursor
        if edges == (_C_R | _C_T) or edges == (_C_L | _C_B):
            return Qt.CursorShape.SizeBDiagCursor
        if edges & (_C_L | _C_R):
            return Qt.CursorShape.SizeHorCursor
        if edges & (_C_T | _C_B):
            return Qt.CursorShape.SizeVerCursor
        return Qt.CursorShape.OpenHandCursor

    def _cardFromWidget(self, widget: QWidget) -> Optional[iCard]:
        lWalk: Optional[QWidget] = widget
        while lWalk is not None:
            if self._grid is not None:
                for lP in self._grid.Model.Placements:
                    if isinstance(lP.Card, QWidget) and (
                        lP.Card is lWalk or lP.Card.isAncestorOf(lWalk)
                    ):
                        return lP.Card
            lWalk = lWalk.parentWidget()
        return None
