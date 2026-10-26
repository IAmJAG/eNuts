# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Any, Callable, Dict

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
# Keys are page ids only. Captions live in title. Devices stay out of this table.
PAGE_AND_MENU: Dict[str, Dict[str, Any]] = {
    "CONTENT": {
        PAGE_DASHBOARD: {
            "title": "Dashboard",
            "description": "Overview and status",
            "icon": "dashboard.png",
        },
        PAGE_TOOLS: {
            "title": "Tools",
            "description": "Dataset gathering tools",
            "icon": "tools.png",
            "MENU": {
                PAGE_KG_RECORDER: {
                    "title": "K&G Recorder",
                    "description": "Keyboard and Gesture Recorder",
                    "icon": "KGRecorder.png",
                },
                PAGE_ANNOTATOR: {
                    "title": "Annotator",
                    "description": "Video/Image Annotator",
                    "icon": "annotation.png",
                },
            },
        },
    },
    "FOOTER": {
        PAGE_SETTINGS: {
            "title": "Settings",
            "description": "System settings",
            "icon": "settings.png",
        },
    },
}


# ==================================================================================
def buildBlankPage(key: str, title: str, description: str = "") -> Page:
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
def _pageBuilders() -> Dict[str, Callable[[str], Page]]:
    """Lazy map of specialised builders (avoids navigation <-> pages import cycle)."""
    from ..pages.__kgRecorderPage import buildKGRecorderPage

    return {
        PAGE_KG_RECORDER: buildKGRecorderPage,
    }


# ==================================================================================
def buildNavigationPages() -> dict[str, Page]:
    pages: dict[str, Page] = {}
    builders = _pageBuilders()

    for sectionName in ("CONTENT", "FOOTER"):
        section = PAGE_AND_MENU.get(sectionName) or {}
        for pageId, entry in _flattenEntries(section):
            if pageId in pages:
                continue
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
