# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from av import InvalidDataError, VideoCodecContext, VideoFrame
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QImage, QKeyEvent, QMouseEvent, QPixmap, QWheelEvent

# ==================================================================================
from jAGQt.widgets.image import Image

# ==================================================================================
from fluxCore.types.interface.packets import iFrame
from fluxCore.types.interface.sockets import iControlSocket


# ==================================================================================
class imageStreamer(Image):
    """Image widget that consumes scrcpy frames and reserves input capture hooks."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._decoder: Optional[VideoCodecContext] = None
        self._controlSocket: Optional[iControlSocket] = None
        self._hasFrame: bool = False
        self._deviceWidth: int = 0
        self._deviceHeight: int = 0
        self._captureInput: bool = True

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)

    # ==================================================================================
    @property
    def Decoder(self) -> Optional[VideoCodecContext]:
        return self._decoder

    @Decoder.setter
    def Decoder(self, decoder: Optional[VideoCodecContext]) -> None:
        self._decoder = decoder

    @property
    def ControlSocket(self) -> Optional[iControlSocket]:
        return self._controlSocket

    @ControlSocket.setter
    def ControlSocket(self, socket: Optional[iControlSocket]) -> None:
        self._controlSocket = socket

    @property
    def DeviceWidth(self) -> int:
        return self._deviceWidth

    @DeviceWidth.setter
    def DeviceWidth(self, width: int) -> None:
        self._deviceWidth = max(0, int(width))

    @property
    def DeviceHeight(self) -> int:
        return self._deviceHeight

    @DeviceHeight.setter
    def DeviceHeight(self, height: int) -> None:
        self._deviceHeight = max(0, int(height))

    @property
    def CaptureInput(self) -> bool:
        return self._captureInput

    @CaptureInput.setter
    def CaptureInput(self, enabled: bool) -> None:
        self._captureInput = bool(enabled)

    # ==================================================================================
    @Slot(object)
    def OnFrame(self, frame: iFrame) -> None:
        """Decode one scrcpy frame and paint it without resetting zoom/pan."""
        if self._decoder is None:
            return

        try:
            lDecoded: VideoFrame | None = frame.decode(self._decoder, toGPU=False)
        except InvalidDataError:
            # Common before the first keyframe / after a mid-stream config update.
            return
        except Exception as ex:
            error(f"[{self.__class__.__name__}] decode failed", ex)
            return

        if lDecoded is None:
            return

        try:
            lArr = lDecoded.to_ndarray(format="rgb24")
            lH, lW, _ = lArr.shape
            lBytes = lArr.tobytes()
            lQImage = QImage(
                lBytes, lW, lH, lW * 3, QImage.Format.Format_RGB888
            ).copy()
        except Exception as ex:
            error(f"[{self.__class__.__name__}] frame convert failed", ex)
            return

        lPixmap = QPixmap.fromImage(lQImage)
        self._setStreamingImage(lPixmap)

        if self._deviceWidth <= 0 or self._deviceHeight <= 0:
            self._deviceWidth = lW
            self._deviceHeight = lH

    def _setStreamingImage(self, pixmap: QPixmap) -> None:
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
    # Coordinate mapping (widget local → device pixels)
    # ==================================================================================
    def _mapToDevice(self, widgetX: float, widgetY: float) -> tuple[int, int] | None:
        """Map a point in widget coordinates onto device pixel space."""
        if self._image is None or self._image.isNull():
            return None
        if self._deviceWidth <= 0 or self._deviceHeight <= 0:
            return None

        lScale = self._zoom / 100.0
        lImgX = (widgetX - self._offset.x()) / lScale
        lImgY = (widgetY - self._offset.y()) / lScale

        lImgW = float(self._image.width())
        lImgH = float(self._image.height())
        if lImgW <= 0 or lImgH <= 0:
            return None

        lDevX = int(lImgX / lImgW * self._deviceWidth)
        lDevY = int(lImgY / lImgH * self._deviceHeight)
        lDevX = max(0, min(lDevX, self._deviceWidth - 1))
        lDevY = max(0, min(lDevY, self._deviceHeight - 1))
        return lDevX, lDevY

    # ==================================================================================
    # Input capture hooks (gesture + key) — ready for control-socket injection
    # ==================================================================================
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if self._captureInput and self._controlSocket is not None:
            lPos = event.position()
            lMapped = self._mapToDevice(lPos.x(), lPos.y())
            if lMapped is not None:
                self._onGesturePress(lMapped[0], lMapped[1], event)
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._captureInput and self._controlSocket is not None and event.buttons():
            lPos = event.position()
            lMapped = self._mapToDevice(lPos.x(), lPos.y())
            if lMapped is not None:
                self._onGestureMove(lMapped[0], lMapped[1], event)
                event.accept()
                return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self._captureInput and self._controlSocket is not None:
            lPos = event.position()
            lMapped = self._mapToDevice(lPos.x(), lPos.y())
            if lMapped is not None:
                self._onGestureRelease(lMapped[0], lMapped[1], event)
                event.accept()
                return
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event: QWheelEvent) -> None:
        if self._captureInput and self._controlSocket is not None:
            lPos = event.position()
            lMapped = self._mapToDevice(lPos.x(), lPos.y())
            if lMapped is not None:
                self._onGestureScroll(lMapped[0], lMapped[1], event)
                event.accept()
                return
        super().wheelEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if self._captureInput and self._controlSocket is not None:
            self._onKeyPress(event)
            event.accept()
            return
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if self._captureInput and self._controlSocket is not None:
            self._onKeyRelease(event)
            event.accept()
            return
        super().keyReleaseEvent(event)

    # ---------------------------------------------------------------------------------
    # Override points for inject-touch / inject-key (leave as stubs for now)
    # ---------------------------------------------------------------------------------
    def _onGesturePress(self, deviceX: int, deviceY: int, event: QMouseEvent) -> None:
        """Hook: touch down at device coordinates. Wire to Touch(eKeyState.DOWN, ...)."""
        pass

    def _onGestureMove(self, deviceX: int, deviceY: int, event: QMouseEvent) -> None:
        """Hook: touch move at device coordinates."""
        pass

    def _onGestureRelease(self, deviceX: int, deviceY: int, event: QMouseEvent) -> None:
        """Hook: touch up at device coordinates."""
        pass

    def _onGestureScroll(self, deviceX: int, deviceY: int, event: QWheelEvent) -> None:
        """Hook: scroll/wheel at device coordinates."""
        pass

    def _onKeyPress(self, event: QKeyEvent) -> None:
        """Hook: key down. Wire to injectKey / InjectKeyPress."""
        pass

    def _onKeyRelease(self, event: QKeyEvent) -> None:
        """Hook: key up. Wire to injectKey / InjectKeyRelease."""
        pass
