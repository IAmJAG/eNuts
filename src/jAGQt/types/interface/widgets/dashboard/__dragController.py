# ==================================================================================
# src/jAGQt/types/interface/widgets/dashboard/__dragController.py
# ==================================================================================
from typing import Protocol, runtime_checkable

# ==================================================================================
from .__dashboardGrid import iDashboardGrid


# ==================================================================================
@runtime_checkable
class iDragController(Protocol):
    """Pointer-driven move interaction; commits via grid TryMove / resolver."""

    def Attach(self, grid: iDashboardGrid) -> None: ...

    def Detach(self) -> None: ...

    @property
    def IsDragging(self) -> bool: ...
