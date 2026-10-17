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
) -> SideBarMenu:
    """Build the eNuts smoke-test navigation menu.

    Structure::

        Dashboard
        Devices
            <deviceNames…>  (or a single placeholder leaf if empty)
        Tools
            Annotator
            Key & Gesture Recorder
        Settings

    Click only prints the item title — no WorkSpace page wiring.
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
    tools.addChild("Key & Gesture Recorder")

    menu.addItem("Settings", role=eSideBarMenuRole.Header)

    menu.itemClicked.connect(_onMenuItemClicked)
    return menu
