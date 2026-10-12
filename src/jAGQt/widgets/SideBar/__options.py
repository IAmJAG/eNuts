# ==================================================================================
from .types import SideBarDockPosition

# ==================================================================================
_ICON_PADDING: int = 2
# ==================================================================================

# ==================================================================================
class sideBarConfig:
    def __init__(self, **kwargs) -> None:
        self._expandedWidth = 240
        self._collapsedWidth = 48

        self._iconSize = self._collapsedWidth - (4 * _ICON_PADDING)
        self._dockPosition = SideBarDockPosition.Left        
        self._isCollapsed: bool = False
        
        self._autoCollapse = False
        self._animationDuration = 220

        for k, v in kwargs.items():
            attrb: str = f"_{k}"
            if not hasattr(self, attrb):
                setattr(self, attrb, v)

    @property
    def expandedWidth(self) -> int:
        return self._expandedWidth

    @property
    def collapsedWidth(self) -> int:
        return self._collapsedWidth

    @property
    def iconSize(self) -> int:
        return self._iconSize

    @property
    def dockPosition(self) -> SideBarDockPosition:
        return self._dockPosition

    @property
    def isCollapsed(self) -> bool:
        return self._isCollapsed

    @property
    def autoCollapse(self) -> bool:
        return self._autoCollapse

    @property
    def animationDuration(self) -> int:
        return self._animationDuration
    