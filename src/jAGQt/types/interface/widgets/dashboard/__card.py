# ==================================================================================
# src/jAGQt/types/interface/widgets/dashboard/__card.py
# ==================================================================================
from typing import Optional, Protocol, runtime_checkable
from uuid import UUID

# ==================================================================================
from ...components import iComponentBase


# ==================================================================================
@runtime_checkable
class iCard(iComponentBase, Protocol):
    """Styleable square shell. Base contract for all dashboard cards."""

    @property
    def Id(self) -> str | UUID: ...

    @property
    def Title(self) -> str: ...

    @Title.setter
    def Title(self, value: str) -> None: ...

    @property
    def MinColSpan(self) -> int: ...

    @MinColSpan.setter
    def MinColSpan(self, value: int) -> None: ...

    @property
    def MinRowSpan(self) -> int: ...

    @MinRowSpan.setter
    def MinRowSpan(self, value: int) -> None: ...

    @property
    def PreferredColSpan(self) -> int: ...

    @PreferredColSpan.setter
    def PreferredColSpan(self, value: int) -> None: ...

    @property
    def PreferredRowSpan(self) -> int: ...

    @PreferredRowSpan.setter
    def PreferredRowSpan(self, value: int) -> None: ...

    @property
    def Variant(self) -> str: ...

    @Variant.setter
    def Variant(self, value: str) -> None: ...

    def SetDragging(self, value: bool) -> None: ...

    def SetResizing(self, value: bool) -> None: ...
