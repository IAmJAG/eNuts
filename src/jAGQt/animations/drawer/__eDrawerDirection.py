# ==================================================================================
from enum import Enum, auto


# ==================================================================================
class eDrawerDirection(Enum):
    """Edge the drawer opens from / closes toward."""

    Left = auto()    # width grows to the right; left edge fixed
    Right = auto()   # width grows to the left; right edge fixed
    Top = auto()     # height grows downward; top edge fixed
    Bottom = auto()  # height grows upward; bottom edge fixed
