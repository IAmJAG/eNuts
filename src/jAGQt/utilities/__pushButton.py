# ==================================================================================
# src/eNuts/UI/__utilities.py
# ==================================================================================
from threading import Lock
from typing import Callable

# ==================================================================================
from PySide6.QtWidgets import QPushButton


# ==================================================================================
class _pushButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lock = Lock()

    def emit(self, signal, /, *args):
        with self._lock:
            try:
                self.setDisabled(True)
                super().emit(signal, *args)

            except Exception as ex:
                raise ex

            finally:
                self.setDisabled(False)
    
# ==================================================================================
def createButton(caption: str, name: str = EMPTY, onClicked: Callable = None, *args, **kwargs) -> QPushButton:
    btn: QPushButton = _pushButton(caption, *args, **kwargs)

    name: str = name if name else f"BTN_{caption.upper()}"
    btn.setObjectName(f"{name.upper()}")

    if onClicked is not None:
        btn.clicked.connect(onClicked)

    return btn