# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import (
    QKeyEvent,
    QMouseEvent,
    QPixmap,
    QResizeEvent,
    QWheelEvent,
)

# ==================================================================================
from jAGQt.widgets.image import Image


# ==================================================================================
class imageStreamer(Image):
    """Streaming image view: paints frames as a background and reports input.

    Responsibilities:
    - Paint a pixmap as a background (zoom/pan preserved across updates).
    - Always fit the image on resize (feature, not an option).
    - Observe keyboard and mouse; emit signals only — never process or inject.

    Non-responsibilities:
    - Decoding, control sockets, device geometry, frame events, key maps.
    """

    TouchPressed = Signal(float, float)
    TouchMoved = Signal(float, float)
    TouchReleased = Signal(float, float)
    WheelScrolled = Signal(float, float, float, float)
    KeyPressed = Signal(int, int)
    KeyReleased = Signal(int, int)
    RightClicked = Signal(float, float)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._hasFrame: bool = False
        self._captureInput: bool = True
        self._touchDown: bool = False

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)

    # ==================================================================================
    @property
    def CaptureInput(self) -> bool:
        return self._captureInput

    @CaptureInput.setter
    def CaptureInput(self, enabled: bool) -> None:
        self._captureInput = bool(enabled)

    # ==================================================================================
    def SetStreamingImage(self, pixmap: QPixmap) -> None:
        """Update pixels without resetView so zoom/pan survive across frames."""
        if pixmap is None or pixmap.isNull():
            return

        self._image = pixmap
        self._dirty = True

        if not self._hasFrame:
            self._hasFrame = True
            self.resetView()
        else:
            self._requestUpdate()

        if self._gl is not None:
            self._gl.setImage(self._image)

    # ==================================================================================
    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        if self._hasFrame and self._image is not None:
            self.resetView()
            self._requestUpdate()

    # ==================================================================================
    def _mapToImage(self, widgetX: float, widgetY: float) -> tuple[float, float] | None:
        """Map widget coordinates onto image pixel space (zoom/pan aware)."""
        if self._image is None or self._image.isNull():
            return None

        lScale = self._zoom / 100.0
        if lScale == 0.0:
            return None

        lImgX = (widgetX - self._offset.x()) / lScale
        lImgY = (widgetY - self._offset.y()) / lScale
        return lImgX, lImgY

    # ==================================================================================
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if self._captureInput:
            lPos = event.position()
            lMapped = self._mapToImage(lPos.x(), lPos.y())
            if lMapped is not None:
                if event.button() == Qt.MouseButton.RightButton:
                    self.RightClicked.emit(lMapped[0], lMapped[1])
                    event.accept()
                    return
                if event.button() == Qt.MouseButton.LeftButton:
                    self._touchDown = True
                    self.TouchPressed.emit(lMapped[0], lMapped[1])
                    event.accept()
                    return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if (
            self._captureInput
            and self._touchDown
            and event.buttons() & Qt.MouseButton.LeftButton
        ):
            lPos = event.position()
            lMapped = self._mapToImage(lPos.x(), lPos.y())
            if lMapped is not None:
                self.TouchMoved.emit(lMapped[0], lMapped[1])
                event.accept()
                return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self._captureInput and event.button() == Qt.MouseButton.LeftButton:
            lPos = event.position()
            lMapped = self._mapToImage(lPos.x(), lPos.y())
            if lMapped is not None:
                self._touchDown = False
                self.TouchReleased.emit(lMapped[0], lMapped[1])
                event.accept()
                return
            if self._touchDown:
                self._touchDown = False
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event: QWheelEvent) -> None:
        if self._captureInput:
            lPos = event.position()
            lMapped = self._mapToImage(lPos.x(), lPos.y())
            if lMapped is not None:
                lAngle = event.angleDelta()
                lH = float(lAngle.x()) / 120.0
                lV = float(lAngle.y()) / 120.0
                if lH != 0.0 or lV != 0.0:
                    self.WheelScrolled.emit(lMapped[0], lMapped[1], lH, lV)
                    event.accept()
                    return
        super().wheelEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if self._captureInput:
            if not event.isAutoRepeat():
                self.KeyPressed.emit(int(event.key()), int(event.modifiers().value))
            event.accept()
            return
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if self._captureInput:
            if not event.isAutoRepeat():
                self.KeyReleased.emit(int(event.key()), int(event.modifiers().value))
            event.accept()
            return
        super().keyReleaseEvent(event)
