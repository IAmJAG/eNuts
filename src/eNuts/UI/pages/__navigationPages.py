# ==================================================================================
from __future__ import annotations

# ==================================================================================
from jAGQt.widgets.page import Page

# ==================================================================================
from .__kgRecorderPage import buildKGRecorderPage
from .__pageKeys import (
    PAGE_ANNOTATOR,
    PAGE_DASHBOARD,
    PAGE_DEVICES,
    PAGE_KG_RECORDER,
    PAGE_SETTINGS,
    PAGE_TOOLS,
)


# ==================================================================================
def buildBlankPage(key: str, title: str, description: str = "") -> Page:
    """Basic Page: header only (title/description). No content widgets."""
    page = Page(title=title, description=description, id=key)
    verbose(f"[pages] blank page key={key!r} title={title!r}")
    return page


# ==================================================================================
def buildNavigationPages() -> dict[str, Page]:
    """Static navigation pages (no live device leaves).

    Device pages are registered at runtime by WorkSpace when discovery reports
    devices. No ``device:none`` placeholder — Devices header alone until leaves
    appear.
    """
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
