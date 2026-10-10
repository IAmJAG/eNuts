# ==================================================================================
# src/jAGQt/types/interface/widgets/dashboard/__layoutResolver.py
# ==================================================================================
from typing import List, Optional, Protocol, Tuple, runtime_checkable

# ==================================================================================
from .__cardPlacement import iCardPlacement
from .__gridModel import iGridModel


# ==================================================================================
@runtime_checkable
class iLayoutResolver(Protocol):
    """Collision resolution: move push, grow shrink-others, shrink self-only.

    Phase 2+ — contract reserved; static grid does not require an implementation yet.
    """

    def ResolveMove(
        self,
        model: iGridModel,
        placement: iCardPlacement,
        newCol: int,
        newRow: int,
    ) -> Optional[List[iCardPlacement]]: ...

    def ResolveGrow(
        self,
        model: iGridModel,
        placement: iCardPlacement,
        newColSpan: int,
        newRowSpan: int,
    ) -> Optional[List[iCardPlacement]]: ...

    def ResolveShrink(
        self,
        model: iGridModel,
        placement: iCardPlacement,
        newColSpan: int,
        newRowSpan: int,
    ) -> Optional[List[iCardPlacement]]: ...
