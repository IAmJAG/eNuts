# ==================================================================================
# src/jAGQt/widgets/dashboard/__cardPlacement.py
# ==================================================================================
from __future__ import annotations

from typing import Tuple

# ==================================================================================
from jAGQt.types.interface.widgets.dashboard import iCard, iCardPlacement


# ==================================================================================
class CardPlacement:
    """Cell-space placement bound to one iCard."""

    def __init__(
        self,
        card: iCard,
        col: int = 0,
        row: int = 0,
        colSpan: int = 1,
        rowSpan: int = 1,
    ) -> None:
        self._card: iCard = card
        self._col: int = max(0, int(col))
        self._row: int = max(0, int(row))
        self._colSpan: int = max(card.MinColSpan, int(colSpan))
        self._rowSpan: int = max(card.MinRowSpan, int(rowSpan))

    @property
    def Card(self) -> iCard:
        return self._card

    @property
    def Col(self) -> int:
        return self._col

    @Col.setter
    def Col(self, value: int) -> None:
        self._col = max(0, int(value))

    @property
    def Row(self) -> int:
        return self._row

    @Row.setter
    def Row(self, value: int) -> None:
        self._row = max(0, int(value))

    @property
    def ColSpan(self) -> int:
        return self._colSpan

    @ColSpan.setter
    def ColSpan(self, value: int) -> None:
        self._colSpan = max(self._card.MinColSpan, int(value))

    @property
    def RowSpan(self) -> int:
        return self._rowSpan

    @RowSpan.setter
    def RowSpan(self, value: int) -> None:
        self._rowSpan = max(self._card.MinRowSpan, int(value))

    def Rect(self) -> Tuple[int, int, int, int]:
        return (self._col, self._row, self._colSpan, self._rowSpan)

    def ContainsCell(self, col: int, row: int) -> bool:
        return (
            self._col <= col < self._col + self._colSpan
            and self._row <= row < self._row + self._rowSpan
        )

    def Intersects(self, other: iCardPlacement) -> bool:
        lC0, lR0, lW0, lH0 = self.Rect()
        lC1, lR1, lW1, lH1 = other.Rect()
        return not (
            lC0 + lW0 <= lC1
            or lC1 + lW1 <= lC0
            or lR0 + lH0 <= lR1
            or lR1 + lH1 <= lR0
        )
