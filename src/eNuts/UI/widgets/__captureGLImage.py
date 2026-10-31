# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Union

# ==================================================================================
from PySide6.QtCore import Qt, Signal, SignalInstance
from PySide6.QtGui import QColor, QFocusEvent, QKeyEvent, QMouseEvent

# ==================================================================================
from jAGQt.widgets.image import GLImage, ImageFitMode


# ==================================================================================
class CaptureGLImage(GLImage):
    """GLImage that surfaces keyboard and mouse events for external handlers.

    Display-only regarding input policy: no recording / inject logic here.
    Controllers (e.g. application KGRecorder) subscribe to the signals.
    """

    keyPressed: SignalInstance = Signal(object)  # QKeyEvent
    keyReleased: SignalInstance = Signal(object)  # QKeyEvent
    mousePressed: SignalInstance = Signal(object)  # QMouseEvent
    mouseMoved: SignalInstance = Signal(object)  # QMouseEvent
    mouseReleased: SignalInstance = Signal(object)  # QMouseEvent

    OBJECT_NAME = "W_CAPTURE_GL_IMAGE"

    def __init__(
        self,
        bg: Union[str, QColor] = "#1a1a1a",
        fitMode: ImageFitMode = ImageFitMode.Scale,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(bg=bg, fitMode=fitMode, *args, **kwargs)
        self.setObjectName(self.OBJECT_NAME)
        # Keyboard focus + move events without requiring a prior press only.
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)

    def focusInEvent(self, event: QFocusEvent) -> None:
        super().focusInEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        self.keyPressed.emit(event)
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        self.keyReleased.emit(event)
        super().keyReleaseEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        # Ensure subsequent key events target this surface.
        if not self.hasFocus():
            self.setFocus(Qt.FocusReason.MouseFocusReason)
        self.mousePressed.emit(event)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self.mouseMoved.emit(event)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.mouseReleased.emit(event)
        super().mouseReleaseEvent(event)
