# ==================================================================================
# src/jAGQt/types/interface/widgets/dashboard/__resizeController.py
# ==================================================================================
from typing import Protocol, runtime_checkable

# ==================================================================================
from .__dashboardGrid import iDashboardGrid


# ==================================================================================
@runtime_checkable
class iResizeController(Protocol):
    """Edge/corner resize; grow may shrink others; shrink is self-only."""

    def Attach(self, grid: iDashboardGrid) -> None: ...

    def Detach(self) -> None: ...

    @property
    def IsResizing(self) -> bool: ...
