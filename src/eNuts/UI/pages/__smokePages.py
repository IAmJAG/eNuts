# ==================================================================================
# Retired — use buildNavigationPages / navigation page keys instead.
# ==================================================================================
from ..navigation import (
    PAGE_ANNOTATOR,
    PAGE_DASHBOARD,
    PAGE_DEVICES,
    PAGE_KG_RECORDER,
    PAGE_SETTINGS,
    PAGE_TOOLS,
    buildBlankPage,
    buildNavigationPages,
    devicePageKey,
)
from ..navigation import G_DEVICE_NONE as C_DEVICE_NONE  # legacy alias

# Legacy alias
PAGE_KEYS = (
    PAGE_DASHBOARD,
    PAGE_DEVICES,
    PAGE_TOOLS,
    PAGE_ANNOTATOR,
    PAGE_KG_RECORDER,
    PAGE_SETTINGS,
)


def buildSmokeTestPages(deviceNames: list[str] | None = None):
    return buildNavigationPages()
