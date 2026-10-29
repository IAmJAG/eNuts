# ==================================================================================
from .__bridge import ScrcpyProxyBridge, ScrcpyRealBridge
from .__footprint import SCRCPYError
from .__messages import (
    ScrcpyErrorMessage,
    ScrcpyInitializeMessage,
    ScrcpyMetadataMessage,
    ScrcpyStartMessage,
    ScrcpyStopMessage,
)
from .__payloads import ScrcpyInitParams

# ==================================================================================
def __getattr__(name: str):
    if name == "SCRCPYEmitter":
        from .__SCRCPYEmitter import SCRCPYEmitter

        return SCRCPYEmitter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# ==================================================================================
__all__ = [
    "SCRCPYEmitter",
    "SCRCPYError",
    "ScrcpyInitParams",
    "ScrcpyInitializeMessage",
    "ScrcpyStartMessage",
    "ScrcpyStopMessage",
    "ScrcpyMetadataMessage",
    "ScrcpyErrorMessage",
    "ScrcpyRealBridge",
    "ScrcpyProxyBridge",
]
