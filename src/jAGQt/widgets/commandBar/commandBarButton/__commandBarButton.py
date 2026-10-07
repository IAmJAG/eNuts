# ==================================================================================
from threading import RLock

# ==================================================================================
from PySide6.QtWidgets import QPushButton

# ==================================================================================
from .__base import _commandBarButtonBase


# ==================================================================================
class CommandBarButton(QPushButton, _commandBarButtonBase):
    OBJECT_NAME = "C_COMMANDBAR_BUTTON"
    def __init__(self, text: str, *args, **kwargs) -> None: 
        OBJNAME: str = kwargs.pop("objectName", self.OBJECT_NAME)
        super().__init__(text=text, objectName=OBJNAME, *args, **kwargs)
        self._lock = RLock()
    