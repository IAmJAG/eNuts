# ==================================================================================
from typing import TYPE_CHECKING, Optional, Protocol, overload, runtime_checkable

# ==================================================================================
if TYPE_CHECKING:
    from .__commandBar import iCommandBar

from .__commandBarGroup import iCommandBarGroup


# ==================================================================================
@runtime_checkable
class iCommandBarButton(Protocol):
    @overload
    def __init__(self, parent: Optional[iCommandBar] = None, *args, **kwargs) -> None: ...
    @overload
    def __init__(self, parent: Optional[iCommandBarGroup] = None, *args, **kwargs) -> None: ...
    def __init__(self, parent: Optional[iCommandBar | iCommandBarGroup] = None, *args, **kwargs) -> None: ...

    def text(self) -> str: ...
    def setText(self, text: str): ...
