# ==================================================================================
from threading import RLock

# ==================================================================================
from PySide6.QtCore import SignalInstance
from PySide6.QtWidgets import QPushButton

# ==================================================================================
from ...components import ObjectName


# ==================================================================================
class CommandBarButton(ObjectName, QPushButton):
    OBJECT_NAME = "C_COMMANDBAR_BUTTON"
    def __init__(self, text: str, *args, **kwargs) -> None: 
        OBJNAME: str = kwargs.pop("objectName", self.OBJECT_NAME)
        super().__init__(text=text, objectName=OBJNAME, *args, **kwargs)
        self._lock = RLock()

    def emit(self: QPushButton, signal: str, *args, **kwargs) -> None:
        with self._lock:
            self.setDisabled(True)
            try:
                _signal: SignalInstance = getattr(self, signal, None)
                if _signal is None or not hasattr(_signal, "emit"):
                    raise AttributeError(
                        f"{type(self).__name__} has no signal named {signal!r}"
                    )
                _signal.emit(*args, **kwargs)

            finally:
                self.setDisabled(False)
    