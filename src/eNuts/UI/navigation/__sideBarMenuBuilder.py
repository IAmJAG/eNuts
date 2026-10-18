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
    """Build smoke-test nav menu + pinned Settings footer item.

    Structure::

        [scroll menu]
          Dashboard          → pageKey=dashboard
          Devices            (header expand only)
              <devices…>     → pageKey=devices
          Tools              (header expand only)
              Annotator      → pageKey=annotator
              K&G Recorder   → pageKey=kg-recorder

        [footer]
          Settings           → pageKey=settings

    Returns ``(menu, settingsItem)``. Navigation is owned by WorkSpace via
    ``pageKeyOf`` + ``itemClicked``.
    """
    menu = SideBarMenu()

    dashboard = menu.addItem("Dashboard", role=eSideBarMenuRole.Leaf)
    _setPageKey(dashboard, PAGE_DASHBOARD)

    devices = menu.addItem("Devices", role=eSideBarMenuRole.Header)
    # Header itself is expand/collapse only; children navigate.
    names = list(deviceNames) if deviceNames else []
    if names:
        for name in names:
            child = devices.addChild(name)
            _setPageKey(child, PAGE_DEVICES)
    else:
        empty = devices.addChild("(no devices)")
        _setPageKey(empty, PAGE_DEVICES)

    tools = menu.addItem("Tools", role=eSideBarMenuRole.Header)
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
