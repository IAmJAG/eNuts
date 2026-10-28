# ==================================================================================
from enum import Enum


# ==================================================================================
class OverloadPolicy(Enum):
    """Outbound queue behaviour when a capacity limit is configured."""

    UNBOUNDED = "unbounded"  # default — no capacity limit (current behaviour)
    BLOCK = "block"  # await put (backpressure)
    DROP_NEW = "drop_new"  # refuse new message when full
    DROP_OLD = "drop_old"  # discard oldest, then enqueue


# ==================================================================================
__all__ = ["OverloadPolicy"]
