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
    devicePageKey,
)

# ==================================================================================
C_PAGE_KEY_PROP = "pageKey"


# ==================================================================================
def _setPageKey(item: SideBarMenuItem, key: str) -> None:
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
def buildSmokeTestSideBarMenu(
    deviceNames: list[str] | None = None,
) -> tuple[SideBarMenu, SideBarMenuItem]:
    """Build nav menu + Settings footer; every node has a pageKey.

    Structure::

        [scroll menu]
          Dashboard              → dashboard
          Devices                → devices   (section summary; still expands)
              <device|none>      → device:<name> | device:none
          Tools                  → tools     (section summary; still expands)
              Annotator          → annotator
              K&G Recorder       → kg-recorder

        [footer]
          Settings               → settings

    Returns ``(menu, settingsItem)``. WorkSpace owns navigation via pageKeyOf.
    """
    menu = SideBarMenu()

    dashboard = menu.addItem("Dashboard", role=eSideBarMenuRole.Leaf)
    _setPageKey(dashboard, PAGE_DASHBOARD)

    devices = menu.addItem("Devices", role=eSideBarMenuRole.Header)
    _setPageKey(devices, PAGE_DEVICES)
    names = list(deviceNames) if deviceNames else []
    if names:
        for name in names:
            child = devices.addChild(name)
            _setPageKey(child, devicePageKey(name))
    else:
        empty = devices.addChild("(no devices)")
        _setPageKey(empty, devicePageKey("(no devices)"))

    tools = menu.addItem("Tools", role=eSideBarMenuRole.Header)
    _setPageKey(tools, PAGE_TOOLS)
    annotator = tools.addChild("Annotator")
    _setPageKey(annotator, PAGE_ANNOTATOR)
    recorder = tools.addChild("K&G Recorder")
    _setPageKey(recorder, PAGE_KG_RECORDER)

    settings = SideBarMenuItem(
        caption="Settings",
        role=eSideBarMenuRole.Header,
    )
    _setPageKey(settings, PAGE_SETTINGS)
    settings.selectionRequested.connect(
        lambda item: menu.selectItem(item) if menu.SelectOnClick else None
    )

    return menu, settings
