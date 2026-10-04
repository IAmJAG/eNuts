# ==================================================================================
# src/jAGQt/widgets/components/__init__.py
# Compatibility re-export after SideBar was moved to widgets/SideBar/
# Prefer: from jAGQt.widgets.SideBar import SideBarItem, ...
# ==================================================================================
from jAGQt.widgets.SideBar.components import (
    IconPosition,
    ItemDisplayMode,
    SeparatorType,
    SideBarContent,
    SideBarGroup,
    SideBarGroupHeader,
    SideBarHeader,
    SideBarIcon,
    SideBarItem,
    SideBarSeparator,
    SideBarText,
)

# ==================================================================================
__all__ = [
    "SideBarIcon",
    "SideBarText",
    "SideBarItem",
    "ItemDisplayMode",
    "IconPosition",
    "SideBarSeparator",
    "SeparatorType",
    "SideBarContent",
    "SideBarHeader",
    "SideBarGroup",
    "SideBarGroupHeader",
]
