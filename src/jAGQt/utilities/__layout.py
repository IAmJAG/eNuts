# ==================================================================================
# src/jAGQtFx/utilities/__layout.py
# ==================================================================================
from typing import Any, List, Set, Tuple

# ==================================================================================
from PySide6.QtCore import QMargins
from PySide6.QtWidgets import QLayout


# ==================================================================================
def newLayout(layout: type[QLayout], spacing=0, margins=(0, 0, 0, 0)) -> QLayout:
    lLayout = layout()
    lLayout.setContentsMargins(*margins)
    lLayout.setSpacing(spacing)    
    return lLayout

def contentMargins(values: List[int] | Tuple[int, ...] | Set[int] | int) -> QMargins:
    if isinstance(values, int):
        return QMargins(values, values, values, values)

    if isinstance(values, Tuple | Set):
        values = list(values)

    # Handle list
    if isinstance(values, list):
        lLen = len(values)
        if lLen == 1:
            return QMargins(values[0], values[0], values[0], values[0])
        
        elif lLen == 2:
            return QMargins(values[0], values[1], values[0], values[1])
        
        elif lLen == 4:
            return QMargins(values[0], values[1], values[2], values[3])

    raise ValueError("Square values must be an int, or a list, tuple, or set of length 1, 2, or 4.")
