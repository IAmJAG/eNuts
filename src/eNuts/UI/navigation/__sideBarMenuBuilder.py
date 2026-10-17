# ==================================================================================
from __future__ import annotations

# ==================================================================================
from jAGQt.widgets.sideBar import SideBarMenu, SideBarMenuItem, eSideBarMenuRole

# ==================================================================================


# ==================================================================================
def _onMenuItemClicked(item: object) -> None:
    """Smoke-test handler: print the item caption (no navigation)."""
    if not isinstance(item, SideBarMenuItem):
        return
    title = item.Caption
    print(f"[SideBarMenu] clicked: {title!r}")
    verbose(f"[SideBarMenu] clicked caption={title!r} role={item.Role!r}")


# ==================================================================================
def buildSmokeTestSideBarMenu(
    deviceNames: list[str] | None = None,
) -> tuple[SideBarMenu, SideBarMenuItem]:
    """Build smoke-test nav menu + pinned Settings footer item.

    Structure::

        [scroll menu]
          Dashboard
          Devices
              <deviceNames…> | (no devices)
          Tools
              Annotator
              Key & Gesture Recorder

        [footer — special]
          Settings

    Returns ``(menu, settingsItem)``. Default icons use the app logo.
    Click only prints the item title — no page wiring.
    """
    menu = SideBarMenu()

    menu.addItem("Dashboard", role=eSideBarMenuRole.Header)

    devices = menu.addItem("Devices", role=eSideBarMenuRole.Header)
    names = list(deviceNames) if deviceNames else []
    if names:
        for name in names:
            devices.addChild(name)
    else:
        devices.addChild("(no devices)")

    tools = menu.addItem("Tools", role=eSideBarMenuRole.Header)
    tools.addChild("Annotator")
    tools.addChild("K&G Recorder")

    # Settings is special: not in the scroll list — pinned footer on SideBar.
    settings = SideBarMenuItem(
        caption="Settings",
        role=eSideBarMenuRole.Header,
    )
    settings.clicked.connect(_onMenuItemClicked)
    settings.selectionRequested.connect(
        lambda item: menu.selectItem(item) if menu.SelectOnClick else None
    )

    menu.itemClicked.connect(_onMenuItemClicked)
    return menu, settings
