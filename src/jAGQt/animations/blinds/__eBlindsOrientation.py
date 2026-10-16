# ==================================================================================
from enum import Enum, auto


# ==================================================================================
class eBlindsOrientation(Enum):
    Horizontal = auto()  # strips stack top→bottom (like horizontal slats)
    Vertical = auto()    # strips side by side
