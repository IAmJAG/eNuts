# ==================================================================================
# src/jAGQt/widgets/dashboard/__dragController.py
# ==================================================================================
from __future__ import annotations

from typing import Optional, TYPE_CHECKING

# ==================================================================================
from PySide6.QtCore import QEvent, QObject, QPoint, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QWidget

# ==================================================================================
from jAGQt.types.interface.widgets.dashboard import iCard

# ==================================================================================
if TYPE_CHECKING:
    from .__dashboardGrid import DashboardGrid


# ==================================================================================
class DragController(QObject):
    """Drag cards on DashboardGrid; cell-snapped move with push via TryMove."""

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._grid: Optional["DashboardGrid"] = None
        self._dragging: bool = False
        self._card: Optional[iCard] = None
        self._pressGlobal: QPoint = QPoint()
        self._originCol: int = 0
        self._originRow: int = 0
        self._grabOffset: QPoint = QPoint()
        self._lastCell: tuple[int, int] = (-1, -1)

    # ----------------------------------------------------------------------------------
    def Attach(self, grid: "DashboardGrid") -> None:
        self.Detach()
        self._grid = grid
        grid.installEventFilter(self)
        for lP in grid.Model.Placements:
            lCard = lP.Card
            if isinstance(lCard, QWidget):
                lCard.installEventFilter(self)
                lCard.setCursor(Qt.CursorShape.OpenHandCursor)

    def Detach(self) -> None:
        if self._grid is not None:
            self._grid.removeEventFilter(self)
            for lP in self._grid.Model.Placements:
                lCard = lP.Card
                if isinstance(lCard, QWidget):
                    lCard.removeEventFilter(self)
                    lCard.unsetCursor()
        self._grid = None
        self._endDrag(commit=False)

    def OnCardAdded(self, card: iCard) -> None:
        if self._grid is None:
            return
        if isinstance(card, QWidget):
            card.installEventFilter(self)
            card.setCursor(Qt.CursorShape.OpenHandCursor)

    def OnCardRemoved(self, card: iCard) -> None:
        if isinstance(card, QWidget):
            card.removeEventFilter(self)
            card.unsetCursor()

    @property
    def IsDragging(self) -> bool:
        return self._dragging

    # ----------------------------------------------------------------------------------
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if self._grid is None:
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
        if lCard is None:
            return False

        lPlacement = self._grid.Model.GetPlacement(lCard)  # type: ignore[union-attr]
        if lPlacement is None:
            return False

        self._dragging = True
        self._card = lCard
        self._originCol = lPlacement.Col
        self._originRow = lPlacement.Row
        self._lastCell = (lPlacement.Col, lPlacement.Row)
        self._pressGlobal = event.globalPosition().toPoint()
        if isinstance(lCard, QWidget):
            lCard.SetDragging(True)
            lCard.setCursor(Qt.CursorShape.ClosedHandCursor)
            lCard.grabMouse()
            lCard.raise_()
            self._grabOffset = event.position().toPoint()
        return True

    def _onMove(self, watched: QObject, event: QMouseEvent) -> bool:
        if not self._dragging or self._card is None or self._grid is None:
            return False

        lPosInGrid = self._grid.mapFromGlobal(event.globalPosition().toPoint())
        lCell = self._grid.CellAt(lPosInGrid.x(), lPosInGrid.y())
        if lCell is None:
            return True

        lCol, lRow = lCell
        if (lCol, lRow) == self._lastCell:
            return True

        if self._grid.TryMove(self._card, lCol, lRow):
            self._lastCell = (lCol, lRow)
        return True

    def _onRelease(self, watched: QObject, event: QMouseEvent) -> bool:
        if not self._dragging:
            return False
        if event.button() != Qt.MouseButton.LeftButton:
            return False
        self._endDrag(commit=True)
        return True

    def _endDrag(self, commit: bool) -> None:
        lCard = self._card
        self._dragging = False
        self._card = None
        self._lastCell = (-1, -1)
        if lCard is not None and isinstance(lCard, QWidget):
            lCard.SetDragging(False)
            lCard.setCursor(Qt.CursorShape.OpenHandCursor)
            if QWidget.mouseGrabber() is lCard:
                lCard.releaseMouse()
        if self._grid is not None:
            self._grid.ApplyLayout()

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
