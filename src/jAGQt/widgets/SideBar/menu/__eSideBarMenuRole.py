# ==================================================================================
from enum import Enum, auto


# ==================================================================================
class eSideBarMenuRole(Enum):
    """Visual/structural role for a menu row (QSS: role=header|leaf)."""

    Header = auto()  # top-level; may own leaf children
    Leaf = auto()
