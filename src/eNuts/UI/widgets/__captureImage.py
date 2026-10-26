# ==================================================================================
from __future__ import annotations

# ==================================================================================
from PySide6.QtCore import Signal, SignalInstance
from PySide6.QtGui import QKeyEvent, QMouseEvent

# ==================================================================================
from jAGQt.widgets.image import Image


# ==================================================================================
class CaptureImage(Image):
    """Plain Image that additionally surfaces keyboard and mouse events.

    Image is display-only (no pan/zoom). Controllers subscribe to the signals;
    this widget only displays and emits.
    """

    keyPressed: SignalInstance = Signal(object)   # QKeyEvent
    keyReleased: SignalInstance = Signal(object)  # QKeyEvent
    mousePressed: SignalInstance = Signal(object)   # QMouseEvent
    mouseMoved: SignalInstance = Signal(object)     # QMouseEvent
    mouseReleased: SignalInstance = Signal(object)  # QMouseEvent

    OBJECT_NAME = "W_CAPTURE_IMAGE"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setObjectName(self.OBJECT_NAME)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        self.keyPressed.emit(event)
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        self.keyReleased.emit(event)
        super().keyReleaseEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.mousePressed.emit(event)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self.mouseMoved.emit(event)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.mouseReleased.emit(event)
        super().mouseReleaseEvent(event)
