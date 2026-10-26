# ==================================================================================
# Compatibility shim — keys live in eNuts.UI.navigation.__pageKeys.
# ==================================================================================
from __future__ import annotations

# ==================================================================================
from ..navigation.__pageKeys import (  # noqa: F401
    G_DEVICE_KEY_PREFIX,
    G_DEVICE_NONE,
    PAGE_ANNOTATOR,
    PAGE_DASHBOARD,
    PAGE_DEVICES,
    PAGE_KG_RECORDER,
    PAGE_SETTINGS,
    PAGE_TOOLS,
    devicePageKey,
    devicePageKeyFromId,
    serialFromPageKey,
)
