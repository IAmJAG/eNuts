# ==================================================================================
# src/jAGQt/types/interface/widgets/dashboard/__gridModel.py
# ==================================================================================
from typing import Dict, List, Optional, Protocol, runtime_checkable
from uuid import UUID

# ==================================================================================
from .__card import iCard
from .__cardPlacement import iCardPlacement


# ==================================================================================
@runtime_checkable
class iGridModel(Protocol):
    """Source of truth for placements and grid metrics (no widgets / no input)."""

    @property
    def Columns(self) -> int: ...

    @Columns.setter
    def Columns(self, value: int) -> None: ...

    @property
    def Gap(self) -> int: ...

    @property
    def CellMinHeight(self) -> int: ...

    @property
    def Placements(self) -> List[iCardPlacement]: ...

    def AddPlacement(self, placement: iCardPlacement) -> bool: ...

    def RemoveByCard(self, card: iCard) -> bool: ...

    def GetPlacement(self, card: iCard) -> Optional[iCardPlacement]: ...

    def Clear(self) -> None: ...

    def ExportLayout(self) -> List[Dict[str, int | str]]: ...

    def RowCount(self) -> int: ...
