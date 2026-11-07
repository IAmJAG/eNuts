# ==================================================================================
from enum import Enum, auto


# ==================================================================================
class eTimeDeltaFormat(Enum):
    SECONDS = auto()
    MILLISECONDS = auto()
    MICROSECONDS = auto()
    NANOSECONDS = auto()

# ==================================================================================
__all__ = ["eTimeDeltaFormat"]