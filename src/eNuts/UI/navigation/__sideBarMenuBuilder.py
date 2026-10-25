# ==================================================================================
from __future__ import annotations

# ==================================================================================
from jAGQt.widgets.sideBar import SideBarMenu, SideBarMenuItem, eSideBarMenuRole

# ==================================================================================
from ..pages import (
    PAGE_ANNOTATOR,
    PAGE_DASHBOARD,
    PAGE_DEVICES,
    PAGE_KG_RECORDER,
    PAGE_SETTINGS,
    PAGE_TOOLS,
)

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
    menu = SideBarMenu()

    # Dashboard    
    dashboard = menu.addItem("Dashboard", role=eSideBarMenuRole.Leaf)

    # Tools
    tools = menu.addItem("Tools", role=eSideBarMenuRole.Header)    
    recorder = tools.addChild("K&G Recorder")
    annotator = tools.addChild("Annotator")    

    # Settings
    settings = SideBarMenuItem(
        caption="Settings",
        role=eSideBarMenuRole.Header,
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
