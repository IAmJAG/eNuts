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
    PAGE_KG_RECORDER,
    PAGE_SETTINGS,
    PAGE_TOOLS,
)

# ==================================================================================
C_DEFAULT_PAGE_TYPE: str = "jAGQt.widgets.page.Page"

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
                    "type": "eNuts.UI.pages.KGRecorder",
                    "commandBar": True,
                },
                PAGE_ANNOTATOR: {
                    "title": "Annotator",
                    "description": "Video/Image Annotator",
                    "icon": "annotation.png",
                    "type": "eNuts.UI.pages.Annotator",
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

def resolvePageClass(typePath: str) -> Type[Page]:
    path = (typePath or "").strip() or C_DEFAULT_PAGE_TYPE
    if "." not in path:
        raise ValueError(
            f"page type must be a full namespace (module.Class), got {path!r}"
        )

    modulePath, _, className = path.rpartition(".")
    module = import_module(modulePath)
    cls = getattr(module, className, None)

    if cls is None:
        raise AttributeError(f"module {modulePath!r} has no attribute {className!r}.")
    
    if not isinstance(cls, type):
        raise TypeError(f"page type {path!r} is not a class.")
    
    return cls

# ==================================================================================
def buildBlankPage(key: str, title: str, description: str = "") -> Page:
    page = Page(title=title, description=description, id=key)
    verbose(f"blank page key={key!r} title={title!r}")
    return page

# ==================================================================================
def _flattenEntries(section: Dict[str, Any]) -> list[tuple[str, Dict[str, Any]]]:
    out: list[tuple[str, Dict[str, Any]]] = []
    for pageId, entry in section.items():
        if not isinstance(entry, dict): continue
        out.append((pageId, entry))
        nested = entry.get("MENU")
        if isinstance(nested, dict):
            out.extend(_flattenEntries(nested))
    return out


# ==================================================================================
def instantiatePage(pageId: str, entry: Dict[str, Any]) -> Page:
    try:
        title = str(entry.get("title") or pageId)
        description = str(entry.get("description") or "")
        typePath = str(entry.get("type") or C_DEFAULT_PAGE_TYPE)
        
        try:
            cls = resolvePageClass(typePath)

        except Exception as ex:
            error(
                f"resolve type={typePath!r} for key={pageId!r} failed: {ex}; "
                f"falling back to {C_DEFAULT_PAGE_TYPE}", ex
            )        
            cls = Page

        commandBarOn = bool(entry.get("commandBar", False))
        try:
            page = cls(
                title = title, description = description,
                commandBarOn = commandBarOn, id = pageId
            )

        except TypeError:
            page = cls(title=title, description=description, id=pageId)

        verbose(f"page key={pageId!r} type={typePath!r} class={cls.__name__}")

    except Exception as ex:
        error(f"build page key={pageId!r} failed", ex)

    finally:
        return page

def buildNavigationPages() -> dict[str, Page]:
    pages: dict[str, Page] = {}
    for sectionName in ("CONTENT", "FOOTER"):
        section = PAGE_AND_MENU.get(sectionName) or {}
        for pageId, entry in _flattenEntries(section):
            if pageId in pages: continue
            pages[pageId] = instantiatePage(pageId, entry)
    
    return pages