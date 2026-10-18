# ==================================================================================
from __future__ import annotations

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QSizePolicy

# ==================================================================================
from jAGQt.widgets.page import Page

# ==================================================================================
# Stable keys shared with the SideBar menu builder (pageKey property).
PAGE_DASHBOARD = "dashboard"
PAGE_DEVICES = "devices"
PAGE_ANNOTATOR = "annotator"
PAGE_KG_RECORDER = "kg-recorder"
PAGE_SETTINGS = "settings"

PAGE_KEYS = (
    PAGE_DASHBOARD,
    PAGE_DEVICES,
    PAGE_ANNOTATOR,
    PAGE_KG_RECORDER,
    PAGE_SETTINGS,
)

# (key, title, description)
_PAGE_SPECS: tuple[tuple[str, str, str], ...] = (
    (PAGE_DASHBOARD, "Dashboard", "Overview and status"),
    (PAGE_DEVICES, "Devices", "Connected and discovered devices"),
    (PAGE_ANNOTATOR, "Annotator", "Annotation tools"),
    (PAGE_KG_RECORDER, "Key & Gesture Recorder", "Capture keys and gestures"),
    (PAGE_SETTINGS, "Settings", "Application preferences"),
)


# ==================================================================================
def buildSmokeTestPages() -> dict[str, Page]:
    """Build placeholder Pages for WorkSpace stack wiring.

    Each page exposes its content layout via ``Page.Layout`` (the inner
    ``W_PAGE_CONTENT`` slot). Header and optional CommandBar stay outside that
    layout by design.
    """
    pages: dict[str, Page] = {}
    for key, title, description in _PAGE_SPECS:
        page = Page(title=title, description=description, id=key)
        body = QLabel(f"{title}\n\n(smoke content)")
        body.setAlignment(Qt.AlignmentFlag.AlignCenter)
        body.setObjectName("W_PAGE_SMOKE_BODY")
        body.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        page.addWidget(body, stretch=1)
        pages[key] = page
        verbose(f"[pages] built page key={key!r} title={title!r} id={page.Id!r}")
    return pages
