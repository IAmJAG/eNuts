# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Dict

# ==================================================================================
from jAGQt.widgets.page import Page

# ==================================================================================
from ..pages.__kgRecorderPage import buildKGRecorderPage
from ..pages.__pageKeys import (
    PAGE_ANNOTATOR,
    PAGE_DASHBOARD,
    PAGE_DEVICES,
    PAGE_KG_RECORDER,
    PAGE_SETTINGS,
    PAGE_TOOLS,
)

PAGE_AND_MENU: Dict = {
    "CONTENT": {
        "Dashboard": {
            "title": "Dashboard",
            "description": "Overview and status",
            "icon": "dashboard.png",
        },
        "Tools":{
            "title": "Tools",
            "description": "Dataset gathering tools",
            "icon": "tools.png",
            "MENU": [
                {
                    "K&G Recorder": {
                        "title": "K&G Recorder",
                        "description": "Keyboard and Gesture Recorder",
                        "icon": "KGRecorder.png",
                    },
                },
                {
                    "Annotator": {
                        "title": "Annotator",
                        "description": "Video/Image Annotator",
                        "icon": "annotation.png",
                    }
                }
            ]
        }
    },
    "FOOTER": {
        "Settings": {
            "title": "Settings",
            "description": "System settings",
            "icon": "settings.png",
        }
    }
}
# ==================================================================================

# ==================================================================================
def buildBlankPage(key: str, title: str, description: str = "") -> Page:
    page = Page(title=title, description=description, id=key)
    verbose(f"[pages] blank page key={key!r} title={title!r}")
    return page

# ==================================================================================
def buildNavigationPages() -> dict[str, Page]:
    pages: dict[str, Page] = {}

    pages[PAGE_DASHBOARD] = buildBlankPage(
        PAGE_DASHBOARD, "Dashboard", "Overview and status"
    )

    pages[PAGE_DEVICES] = buildBlankPage(
        PAGE_DEVICES, "Devices", "Device summary"
    )
    pages[PAGE_TOOLS] = buildBlankPage(
        PAGE_TOOLS, "Tools", "Tools summary"
    )
    pages[PAGE_ANNOTATOR] = buildBlankPage(
        PAGE_ANNOTATOR, "Annotator", "Annotation tools"
    )
    pages[PAGE_KG_RECORDER] = buildKGRecorderPage(PAGE_KG_RECORDER)
    pages[PAGE_SETTINGS] = buildBlankPage(
        PAGE_SETTINGS, "Settings", "Application preferences"
    )

    return pages
