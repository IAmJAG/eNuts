# ==================================================================================
from .__bridge import ScrcpyProxyBridge, ScrcpyRealBridge
from .__footprint import SCRCPYError
from .__frameRing import FrameRing
from .__frameSlot import (
    C_DEFAULT_RING_SIZE,
    C_FRAME_SLOT_HEADER_SIZE,
    C_FRAME_SLOT_MAGIC,
    C_MAX_RING_SIZE,
    C_MIN_RING_SIZE,
    FramePresentFormat,
    FrameSlotFlags,
    FrameSlotHeader,
    clampRingSize,
    makeFrameSlotHeader,
    nextRingIndex,
    pickWriteIndex,
    shouldSkipPresent,
)
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
    "C_FRAME_SLOT_MAGIC",
    "C_FRAME_SLOT_HEADER_SIZE",
    "C_DEFAULT_RING_SIZE",
    "C_MIN_RING_SIZE",
    "C_MAX_RING_SIZE",
    "FramePresentFormat",
    "FrameSlotFlags",
    "FrameSlotHeader",
    "FrameRing",
    "makeFrameSlotHeader",
    "clampRingSize",
    "nextRingIndex",
    "pickWriteIndex",
    "shouldSkipPresent",
]
