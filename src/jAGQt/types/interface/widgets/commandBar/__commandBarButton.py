# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtWidgets import QAbstractButton

# ==================================================================================
from ..commandBar import iCommandBar, iCommandBarGroup


# ==================================================================================
class iCommandBarButton(QAbstractButton):
    def __init__(self, parent: Optional[iCommandBar | iCommandBarGroup] = None, *args, **kwargs) -> None: ...