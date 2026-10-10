# ==================================================================================
# src/jAGQt/widgets/dashboard/__options.py
# ==================================================================================


# ==================================================================================
class dashboardConfig:
    def __init__(self, **kwargs) -> None:
        self._columns: int = 4
        self._gap: int = 12
        self._cellMinHeight: int = 120
        self._margins: int = 12

        for k, v in kwargs.items():
            attrb: str = f"_{k}"
            if hasattr(self, attrb):
                setattr(self, attrb, v)

    @property
    def columns(self) -> int:
        return self._columns

    @property
    def gap(self) -> int:
        return self._gap

    @property
    def cellMinHeight(self) -> int:
        return self._cellMinHeight

    @property
    def margins(self) -> int:
        return self._margins
