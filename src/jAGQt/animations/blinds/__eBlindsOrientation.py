# ==================================================================================
from enum import Enum, auto


# ==================================================================================
class eBlindsOrientation(Enum):
    Horizontal = auto()  # animate height in strip steps
    Vertical = auto()    # animate width in strip steps
