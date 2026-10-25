# ==================================================================================
# Retired — use buildNavigationPages / __pageKeys instead.
# ==================================================================================
from ..navigation.__navigation import buildBlankPage, buildNavigationPages
from .__pageKeys import (
    C_DEVICE_NONE,
    PAGE_ANNOTATOR,
    PAGE_DASHBOARD,
    PAGE_DEVICES,
    PAGE_KG_RECORDER,
    PAGE_SETTINGS,
    PAGE_TOOLS,
    devicePageKey,
)

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
    return buildNavigationPages(deviceNames)
