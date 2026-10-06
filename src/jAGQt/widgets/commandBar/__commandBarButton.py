# ==================================================================================
# src/jAGQt/widgets/commandBar/__commandBarButton.py
# ==================================================================================
from threading import RLock
from typing import Optional

# ==================================================================================
from PySide6.QtWidgets import QPushButton

# ==================================================================================
from ...types.interface.widgets.commandBar import iCommandBar, iCommandBarGroup


# ==================================================================================
class CommandBarButton(QPushButton):
    OBJECT_NAME = "C_COMMANDBAR_BUTTON"
    def __init__(self, parent: Optional[iCommandBar | iCommandBarGroup] = None, *args, **kwargs) -> None:
        OBJNAME: str = self.OBJECT_NAME
        super().__init__(parent=parent, objectName=OBJNAME, *args, **kwargs)
        self._lock = RLock()

    def emit(self, signal: str, *args, **kwargs):
        with self._lock:
            try:
                self.setDisabled(True)
                super().emit(signal, *args, **kwargs)

            except Exception as ex:
                raise ex

            finally:
                self.setDisabled(False)
    