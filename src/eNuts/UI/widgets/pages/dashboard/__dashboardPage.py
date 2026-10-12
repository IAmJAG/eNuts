# ==================================================================================
from __future__ import annotations

# ==================================================================================
from jAGQt.widgets import Page
from jAGQt.widgets.dashboard import DashboardGrid

# ==================================================================================
C_PAGE_ID_DASHBOARD: str = "dashboard"
# ==================================================================================


# ==================================================================================
class DashboardPage(Page):
    """Main dashboard host — DashboardGrid fills the page content area."""

    def __init__(self, parent=None) -> None:
        super().__init__(
            title="Dashboard",
            description="Overview",
            id=C_PAGE_ID_DASHBOARD,
            parent=parent,
        )
        self.setObjectName("DashboardPage")

        self._grid: DashboardGrid = DashboardGrid(parent=self)
        self.addWidget(self._grid)

    @property
    def Grid(self) -> DashboardGrid:
        return self._grid
