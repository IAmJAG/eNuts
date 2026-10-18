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
C_PAGE_KEY_PROP = "pageKey"


# ==================================================================================
def setPageKey(item: SideBarMenuItem, key: str) -> None:
    item.setProperty(C_PAGE_KEY_PROP, key)


# ==================================================================================
def pageKeyOf(item: object) -> str | None:
    """Read the navigation key attached to a SideBarMenuItem, if any."""
    if not isinstance(item, SideBarMenuItem):
        return None
    value = item.property(C_PAGE_KEY_PROP)
    if value is None:
        return None
    key = str(value).strip()
    return key or None


# ==================================================================================
def buildSmokeTestSideBarMenu() -> tuple[SideBarMenu, SideBarMenuItem, SideBarMenuItem]:
    """Build nav menu + Settings footer; every static node has a pageKey.

    Returns ``(menu, settingsItem, devicesHeader)``.

    Devices starts with **no** children. WorkSpace adds leaves only when
    deviceManager reports real devices (no ``(no devices)`` placeholder).
    """
    menu = SideBarMenu()

    dashboard = menu.addItem("Dashboard", role=eSideBarMenuRole.Leaf)
    setPageKey(dashboard, PAGE_DASHBOARD)

    devices = menu.addItem("Devices", role=eSideBarMenuRole.Header)
    setPageKey(devices, PAGE_DEVICES)
    # Intentionally no children until discovery.

    tools = menu.addItem("Tools", role=eSideBarMenuRole.Header)
    setPageKey(tools, PAGE_TOOLS)
    annotator = tools.addChild("Annotator")
    setPageKey(annotator, PAGE_ANNOTATOR)
    recorder = tools.addChild("K&G Recorder")
    setPageKey(recorder, PAGE_KG_RECORDER)

    settings = SideBarMenuItem(
        caption="Settings",
        role=eSideBarMenuRole.Header,
    )
    setPageKey(settings, PAGE_SETTINGS)
    settings.selectionRequested.connect(
        lambda item: menu.selectItem(item) if menu.SelectOnClick else None
    )

    return menu, settings, devices
