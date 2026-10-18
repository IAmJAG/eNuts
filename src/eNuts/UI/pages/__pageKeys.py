# ==================================================================================
from __future__ import annotations

# ==================================================================================
# Stable navigation keys. Device leaves use devicePageKeyFromId(serial).

PAGE_DASHBOARD = "dashboard"
PAGE_DEVICES = "devices"
PAGE_TOOLS = "tools"
PAGE_ANNOTATOR = "annotator"
PAGE_KG_RECORDER = "kg-recorder"
PAGE_SETTINGS = "settings"

C_DEVICE_KEY_PREFIX = "device:"
C_DEVICE_NONE = "device:none"


# ==================================================================================
def devicePageKeyFromId(deviceId: str) -> str:
    """Stable pageKey from device id/serial."""
    cleaned = (deviceId or "").strip()
    if not cleaned:
        return C_DEVICE_NONE
    return f"{C_DEVICE_KEY_PREFIX}{cleaned}"


# ==================================================================================
def devicePageKey(nameOrId: str) -> str:
    """Legacy helper: treat empty / '(no devices)' as none; else device:<value>."""
    cleaned = (nameOrId or "").strip()
    if not cleaned or cleaned == "(no devices)":
        return C_DEVICE_NONE
    return f"{C_DEVICE_KEY_PREFIX}{cleaned}"
