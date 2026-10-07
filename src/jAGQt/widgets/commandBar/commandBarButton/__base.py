# ==================================================================================
from PySide6.QtWidgets import QPushButton


# ==================================================================================
class _commandBarButtonBase:
    def emit(self: QPushButton, signal: str, *args, **kwargs) -> None:
        with self._lock:
            self.setDisabled(True)
            try:
                lSig = getattr(self, signal, None)
                if lSig is None or not hasattr(lSig, "emit"):
                    raise AttributeError(
                        f"{type(self).__name__} has no signal named {signal!r}"
                    )
                lSig.emit(*args, **kwargs)
            finally:
                self.setDisabled(False)
