# ==================================================================================
# src/jAGQt/widgets/commandBar/__commandBarButton.py
# ==================================================================================
from threading import RLock
from typing import Optional, Protocol, runtime_checkable

# ==================================================================================
from PySide6.QtWidgets import QPushButton

# ==================================================================================
from ....types.interface.widgets.commandBar import (
    iCommandBar,
    iCommandBarGroup,
)
from .__base import _commandBarButtonBase


# ==================================================================================
class CommandBarButton(QPushButton, _commandBarButtonBase):
    OBJECT_NAME = "C_COMMANDBAR_BUTTON"
    def __init__(self, caption: str, parent: Optional[iCommandBar | iCommandBarGroup] = None, *args, **kwargs) -> None:
        OBJNAME: str = kwargs.pop("objectName", self.OBJECT_NAME)
        super().__init__(text=caption, parent=parent, objectName=OBJNAME, *args, **kwargs)
        self._lock = RLock()
    