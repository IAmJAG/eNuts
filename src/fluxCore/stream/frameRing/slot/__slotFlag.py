# ==================================================================================
from __future__ import annotations

# ==================================================================================
from enum import Enum, auto


# ==================================================================================
class eSlotFlag(Enum):
    EMPTY = auto()  # never used or cleared
    FREE = auto()  # released after sequential readers advanced
    WRITING = auto()  # decode/convert in progress
    FILLED = auto()  # valid cached payload; readable


# ==================================================================================
__all__ = ["eSlotFlag"]
# ==================================================================================