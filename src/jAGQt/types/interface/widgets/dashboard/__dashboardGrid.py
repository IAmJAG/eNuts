# ==================================================================================
# src/jAGQt/types/interface/widgets/dashboard/__dashboardGrid.py
# ==================================================================================
from typing import List, Optional, Protocol, runtime_checkable

# ==================================================================================
from ...components import iComponentBase
from .__card import iCard
from .__cardPlacement import iCardPlacement
from .__gridModel import iGridModel


# ==================================================================================
@runtime_checkable
class iDashboardGrid(iComponentBase, Protocol):
    """Host widget: model → geometry → card children."""

    @property
    def Model(self) -> iGridModel: ...

    def AddCard(
        self,
        card: iCard,
        col: Optional[int] = None,
        row: Optional[int] = None,
        colSpan: Optional[int] = None,
        rowSpan: Optional[int] = None,
    ) -> Optional[iCardPlacement]: ...

    def RemoveCard(self, card: iCard) -> bool: ...

    def Clear(self) -> None: ...

    def TryMove(self, card: iCard, col: int, row: int) -> bool: ...

    def TryResize(self, card: iCard, colSpan: int, rowSpan: int) -> bool: ...

    def ApplyLayout(self) -> None: ...
