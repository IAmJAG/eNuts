# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Any, Dict, Optional

# ==================================================================================
from jAGQt.widgets.sideBar import SideBarMenu, SideBarMenuItem, eSideBarMenuRole
from utilities.io import getICONPath

# ==================================================================================
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
def _iconOf(entry: Dict[str, Any]) -> Optional[str]:
    name = entry.get("icon")
    if not name:
        return None
    return getICONPath(str(name))

# ==================================================================================
def _addEntry(
    parent: SideBarMenu | SideBarMenuItem, pageId: str, entry: Dict[str, Any],
    *, asHeader: bool
) -> SideBarMenuItem:
    title = str(entry.get("title") or pageId)
    icon = _iconOf(entry)
    role = eSideBarMenuRole.Header if asHeader else eSideBarMenuRole.Leaf

    if isinstance(parent, SideBarMenu):
        item = parent.addItem(title, role=role, icon=icon)

    else:
        item = parent.addChild(title, icon=icon)

    setPageKey(item, pageId)

    nested = entry.get("MENU")
    if isinstance(nested, dict):
        for childId, childEntry in nested.items():
            if isinstance(childEntry, dict):
                _addEntry(item, childId, childEntry, asHeader=False)

    return item


# ==================================================================================
def buildSideBarMenu(
    structure: Optional[Dict[str, Dict[str, Any]]] = None
) -> tuple[SideBarMenu, Optional[SideBarMenuItem]]:
    """
    Build content + footer from PAGE_AND_MENU (or an injected structure).
    Returns (contentMenu, footerItem). Footer is the last FOOTER entry when
    present; callers may wire selectionRequested on it.
    """
    data = structure if structure is not None else PAGE_AND_MENU
    menu: SideBarMenu = SideBarMenu()

    content = data.get("CONTENT") or {}
    for pageId, entry in content.items():
        if isinstance(entry, dict):
            _addEntry(menu, pageId, entry, asHeader=True)

    footerItem: Optional[SideBarMenuItem] = None
    footer = data.get("FOOTER") or {}
    for pageId, entry in footer.items():
        if not isinstance(entry, dict): continue
        title = str(entry.get("title") or pageId)
        footerItem = SideBarMenuItem(
            caption = title,
            role = eSideBarMenuRole.Header,
            icon = _iconOf(entry),
        )

        setPageKey(footerItem, pageId)
        
        footerItem.selectionRequested.connect(
            lambda item, m=menu: m.selectItem(item) if m.SelectOnClick else None
        )

    return menu, footerItem
