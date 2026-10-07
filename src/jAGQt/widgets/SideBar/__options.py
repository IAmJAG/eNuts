# ==================================================================================
from ...types import DockPosition

# ==================================================================================
_ICON_PADDING: int = 2
# ==================================================================================

# ==================================================================================
class sideBarConfig:
    def __init__(self, **kwargs) -> None:
        self._expandedWidth = 240
        self._collapsedWidth = 48
        self._iconSize = self._collapsedWidth - (4 * _ICON_PADDING)
        self._dockPosition = DockPosition.Left
        self._startCollapsed = False
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
    def dockPosition(self) -> DockPosition:
        return self._dockPosition

    @property
    def startCollapsed(self) -> bool:
        return self._startCollapsed

    @property
    def autoCollapse(self) -> bool:
        return self._autoCollapse

    @property
    def animationDuration(self) -> int:
        return self._animationDuration
    