# ==================================================================================
# src/jAGQt/widgets/dashboard/__options.py
# ==================================================================================


# ==================================================================================
class dashboardConfig:
    """Grid metrics. cellSize is the fixed icon-unit (default 64x64).

    columns is only a seed / fallback. At runtime DashboardGrid derives the
    live column count from available width so the unit grid reaches the edges.
    """

    def __init__(self, **kwargs) -> None:
        self._columns: int = 12  # seed until first resize
        self._minColumns: int = 1
        self._gap: int = 8
        self._cellSize: int = 64
        self._margins: int = 8

        for k, v in kwargs.items():
            attrb: str = f"_{k}"
            if hasattr(self, attrb):
                setattr(self, attrb, v)

        # Back-compat: cellMinHeight maps to cellSize if provided alone
        if "cellMinHeight" in kwargs and "cellSize" not in kwargs:
            self._cellSize = max(1, int(kwargs["cellMinHeight"]))

    @property
    def columns(self) -> int:
        return self._columns

    @property
    def minColumns(self) -> int:
        return max(1, int(self._minColumns))

    @property
    def gap(self) -> int:
        return self._gap

    @property
    def cellSize(self) -> int:
        return self._cellSize

    @property
    def cellMinHeight(self) -> int:
        """Alias for cellSize (height of one cell unit)."""
        return self._cellSize

    @property
    def margins(self) -> int:
        return self._margins
