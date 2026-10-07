# ==================================================================================
from typing import Callable, Optional, Protocol, runtime_checkable

# ==================================================================================
from ...components import iComponentBase
from .__sideBarItem import iSideBarItem


# ==================================================================================
@runtime_checkable
class iSideBar(iComponentBase, Protocol):
    def __init__(self, title: str, description: str, *args, **kwargs,) -> None:...
    def AddItem(self, text: str = "", callback: Optional[Callable] = None) -> iSideBarItem: ...