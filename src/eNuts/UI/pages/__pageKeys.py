# ==================================================================================
from __future__ import annotations

# ==================================================================================
# Stable navigation keys. Device leaves use devicePageKey(name).

PAGE_DASHBOARD = "dashboard"
PAGE_DEVICES = "devices"
PAGE_TOOLS = "tools"
PAGE_ANNOTATOR = "annotator"
PAGE_KG_RECORDER = "kg-recorder"
PAGE_SETTINGS = "settings"

C_DEVICE_KEY_PREFIX = "device:"
C_DEVICE_NONE = "device:none"


# ==================================================================================
def devicePageKey(name: str) -> str:
    """Stable pageKey for a device leaf (or placeholder)."""
    cleaned = (name or "").strip()
    if not cleaned or cleaned == "(no devices)":
        return C_DEVICE_NONE
    return f"{C_DEVICE_KEY_PREFIX}{cleaned}"
