# ==================================================================================
from __future__ import annotations

# ==================================================================================
from importlib import import_module
from typing import Any, Dict, Type

# ==================================================================================
from jAGQt.widgets.page import Page

# ==================================================================================
from .__pageKeys import (
    PAGE_ANNOTATOR,
    PAGE_DASHBOARD,
    PAGE_DEVICES,
    PAGE_KG_RECORDER,
    PAGE_SETTINGS,
    PAGE_TOOLS,
)

# ==================================================================================
# Default when an entry omits "type". Full dotted path to a Page subclass.
C_DEFAULT_PAGE_TYPE: str = "jAGQt.widgets.page.Page"

# Keys are page ids only. Captions live in title. Devices stay out of this table.
# "type" is a full class namespace resolved at load time (importlib).
PAGE_AND_MENU: Dict[str, Dict[str, Any]] = {
    "CONTENT": {
        PAGE_DASHBOARD: {
            "title": "Dashboard",
            "description": "Overview and status",
            "icon": "dashboard.png",
            "type": "jAGQt.widgets.page.Page",
        },
        PAGE_TOOLS: {
            "title": "Tools",
            "description": "Dataset gathering tools",
            "icon": "tools.png",
            "type": "jAGQt.widgets.page.Page",
            "MENU": {
                PAGE_KG_RECORDER: {
                    "title": "K&G Recorder",
                    "description": "Keyboard and Gesture Recorder",
                    "icon": "KGRecorder.png",
                    # Stripped to base Page; later → eNuts…KGRecorderPage
                    "type": "jAGQt.widgets.page.Page",
                },
                PAGE_ANNOTATOR: {
                    "title": "Annotator",
                    "description": "Video/Image Annotator",
                    "icon": "annotation.png",
                    "type": "jAGQt.widgets.page.Page",
                },
            },
        },
    },
    "FOOTER": {
        PAGE_SETTINGS: {
            "title": "Settings",
            "description": "System settings",
            "icon": "settings.png",
            "type": "jAGQt.widgets.page.Page",
        },
    },
}


# ==================================================================================
def buildBlankPage(key: str, title: str, description: str = "", icon: str = "") -> Page:
    page = Page(title=title, description=description, id=key)
    verbose(f"[pages] blank page key={key!r} title={title!r}")
    return page


# ==================================================================================
def _flattenEntries(section: Dict[str, Any]) -> list[tuple[str, Dict[str, Any]]]:
    """Yield (pageId, entry) depth-first; nested MENU is also keyed by page id."""
    out: list[tuple[str, Dict[str, Any]]] = []
    for pageId, entry in section.items():
        if not isinstance(entry, dict):
            continue
        out.append((pageId, entry))
        nested = entry.get("MENU")
        if isinstance(nested, dict):
            out.extend(_flattenEntries(nested))
    return out


# ==================================================================================
def _instantiatePage(pageId: str, entry: Dict[str, Any]) -> Page:
    title = str(entry.get("title") or pageId)
    description = str(entry.get("description") or "")
    typePath = str(entry.get("type") or C_DEFAULT_PAGE_TYPE)
    try:
        cls = resolvePageClass(typePath)
    except Exception as ex:
        warning(
            f"[pages] resolve type={typePath!r} for key={pageId!r} failed: {ex}; "
            f"falling back to {C_DEFAULT_PAGE_TYPE}"
        )
        cls = Page

    # Compatible with Page(title, description, commandBarOn=False, id=...)
    commandBarOn = bool(entry.get("commandBar", False))
    try:
        page = cls(
            title=title,
            description=description,
            commandBarOn=commandBarOn,
            id=pageId,
        )
    except TypeError:
        # Subclasses may not accept commandBarOn yet.
        page = cls(title=title, description=description, id=pageId)

    verbose(
        f"[pages] page key={pageId!r} type={typePath!r} class={cls.__name__}"
    )
    return page


# ==================================================================================
def buildNavigationPages() -> dict[str, Page]:
    """Build the static page stack from PAGE_AND_MENU via entry['type'] namespaces."""
    pages: dict[str, Page] = {}

    for sectionName in ("CONTENT", "FOOTER"):
        section = PAGE_AND_MENU.get(sectionName) or {}
        for pageId, entry in _flattenEntries(section):
            if pageId in pages: continue
            title = str(entry.get("title") or pageId)
            description = str(entry.get("description") or "")
            builder = builders.get(pageId)
            if builder is not None:
                pages[pageId] = builder(pageId)
            else:
                pages[pageId] = buildBlankPage(pageId, title, description)

    # Devices header page is still registered for stack lookup; leaves are dynamic.
    if PAGE_DEVICES not in pages:
        pages[PAGE_DEVICES] = buildBlankPage(
            PAGE_DEVICES, "Devices", "Device summary"
        )

    return pages
