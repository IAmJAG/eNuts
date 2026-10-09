# ==================================================================================
# src/jAGQt/widgets/header/__iconPosition.py
# ==================================================================================
from enum import Enum, auto


# ==================================================================================
class IconPosition(Enum):
    """Where the header icon sits relative to title / description."""

    TitleRow = auto()  # Format 1: icon + title on row 1; description full-width below
    SpanRows = auto()  # Format 2: icon left column spanning both rows
