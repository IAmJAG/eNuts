# ==================================================================================
from typing import TYPE_CHECKING, Optional, Protocol, overload, runtime_checkable


# ==================================================================================
@runtime_checkable
class iCommandBarButton(Protocol):
    def __init__(self, text: str, *args, **kwargs) -> None: ...
    def text(self) -> str: ...
    def setText(self, text: str): ...
