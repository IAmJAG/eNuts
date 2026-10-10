# ==================================================================================
# src/jAGQt/types/interface/widgets/dashboard/__cardPlacement.py
# ==================================================================================
from typing import Protocol, runtime_checkable, Tuple

# ==================================================================================
from .__card import iCard


# ==================================================================================
@runtime_checkable
class iCardPlacement(Protocol):
    """Cell-space placement of one card (no pixel geometry)."""

    @property
    def Card(self) -> iCard: ...

    @property
    def Col(self) -> int: ...

    @Col.setter
    def Col(self, value: int) -> None: ...

    @property
    def Row(self) -> int: ...

    @Row.setter
    def Row(self, value: int) -> None: ...

    @property
    def ColSpan(self) -> int: ...

    @ColSpan.setter
    def ColSpan(self, value: int) -> None: ...

    @property
    def RowSpan(self) -> int: ...

    @RowSpan.setter
    def RowSpan(self, value: int) -> None: ...

    def Rect(self) -> Tuple[int, int, int, int]:
        """(col, row, colSpan, rowSpan)."""
        ...

    def ContainsCell(self, col: int, row: int) -> bool: ...

    def Intersects(self, other: "iCardPlacement") -> bool: ...
