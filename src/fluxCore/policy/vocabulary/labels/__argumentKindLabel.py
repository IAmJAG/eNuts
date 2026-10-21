# ==================================================================================
from __future__ import annotations

# ==================================================================================
from ..__label import Label


# ==================================================================================
class ArgumentKindLabel(Label):
    def __init__(self, id: str = "", description: str = "") -> None:
        super().__init__(id, description)

    @property
    def vocabularyKey(self) -> str:
        return f"{self._id}"
