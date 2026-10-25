# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Dict

# ==================================================================================
from jAGQt.widgets.sideBar import SideBarMenu, SideBarMenuItem, eSideBarMenuRole
from utilities.io import getICONPath

# ==================================================================================
from ..pages import (
    PAGE_ANNOTATOR,
    PAGE_DASHBOARD,
    PAGE_KG_RECORDER,
    PAGE_SETTINGS,
    PAGE_TOOLS,
)
from .__navigation import PAGE_AND_MENU

# ==================================================================================
G_PAGE_KEY_PROP = "pageKey"

# ==================================================================================
def setPageKey(item: SideBarMenuItem, key: str) -> None:
    item.setProperty(G_PAGE_KEY_PROP, key)

# ==================================================================================
def pageKeyOf(item: object) -> str | None:
    """Read the navigation key attached to a SideBarMenuItem, if any."""
    if not isinstance(item, SideBarMenuItem): return None
    value = item.property(G_PAGE_KEY_PROP)

    if value is None: return None
    
    key = str(value).strip()
    return key or None


# ==================================================================================
def buildSideBarMenu() -> tuple[SideBarMenu, SideBarMenuItem]:
    menu: SideBarMenu = SideBarMenu()

    # Dashboard
    dashboard = menu.addItem(
        "Dashboard", 
        role=eSideBarMenuRole.Header, 
        icon=getICONPath("dashboard.png")
    )

    # Tools
    tools = menu.addItem(
        "Tools", 
        role=eSideBarMenuRole.Header,
        icon=getICONPath("tools.png")
    )    
    recorder = tools.addChild("K&G Recorder", icon=getICONPath("KGRecorder.png"),)
    annotator = tools.addChild("Annotator", icon=getICONPath("annotation.png"),)

    # Settings
    settings = SideBarMenuItem(
        caption="Settings",
        role=eSideBarMenuRole.Header,
        icon=getICONPath("settings.png"),
    )

    setPageKey(dashboard, PAGE_DASHBOARD)

    setPageKey(tools, PAGE_TOOLS)
    setPageKey(recorder, PAGE_KG_RECORDER)
    setPageKey(annotator, PAGE_ANNOTATOR)
    
    setPageKey(settings, PAGE_SETTINGS)
    
    settings.selectionRequested.connect(
        lambda item: menu.selectItem(item) if menu.SelectOnClick else None
    )

    return menu, settings
