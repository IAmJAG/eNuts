# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from av import InvalidDataError, VideoCodecContext, VideoFrame
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import (
    QImage,
    QKeyEvent,
    QMouseEvent,
    QPixmap,
    QResizeEvent,
    QWheelEvent,
)

# ==================================================================================
from jAGQt.widgets.image import Image

# ==================================================================================
from fluxCore.action.android.enums import eKeyCode, eKeyState, eMetaState
from fluxCore.action.android.gesture import Scroll, Touch
from fluxCore.action.android.injectKey import InjectKeyPress, InjectKeyRelease
from fluxCore.types.geometry import Point
from fluxCore.types.interface.packets import iFrame
from fluxCore.types.interface.sockets import iControlSocket

# ==================================================================================
# Qt key → Android keycode (subset used for interactive control)
# ==================================================================================
_C_QT_TO_ANDROID: dict[int, eKeyCode] = {
    Qt.Key.Key_0: eKeyCode.KEYCODE_0,
    Qt.Key.Key_1: eKeyCode.KEYCODE_1,
    Qt.Key.Key_2: eKeyCode.KEYCODE_2,
    Qt.Key.Key_3: eKeyCode.KEYCODE_3,
    Qt.Key.Key_4: eKeyCode.KEYCODE_4,
    Qt.Key.Key_5: eKeyCode.KEYCODE_5,
    Qt.Key.Key_6: eKeyCode.KEYCODE_6,
    Qt.Key.Key_7: eKeyCode.KEYCODE_7,
    Qt.Key.Key_8: eKeyCode.KEYCODE_8,
    Qt.Key.Key_9: eKeyCode.KEYCODE_9,
    Qt.Key.Key_A: eKeyCode.KEYCODE_A,
    Qt.Key.Key_B: eKeyCode.KEYCODE_B,
    Qt.Key.Key_C: eKeyCode.KEYCODE_C,
    Qt.Key.Key_D: eKeyCode.KEYCODE_D,
    Qt.Key.Key_E: eKeyCode.KEYCODE_E,
    Qt.Key.Key_F: eKeyCode.KEYCODE_F,
    Qt.Key.Key_G: eKeyCode.KEYCODE_G,
    Qt.Key.Key_H: eKeyCode.KEYCODE_H,
    Qt.Key.Key_I: eKeyCode.KEYCODE_I,
    Qt.Key.Key_J: eKeyCode.KEYCODE_J,
    Qt.Key.Key_K: eKeyCode.KEYCODE_K,
    Qt.Key.Key_L: eKeyCode.KEYCODE_L,
    Qt.Key.Key_M: eKeyCode.KEYCODE_M,
    Qt.Key.Key_N: eKeyCode.KEYCODE_N,
    Qt.Key.Key_O: eKeyCode.KEYCODE_O,
    Qt.Key.Key_P: eKeyCode.KEYCODE_P,
    Qt.Key.Key_Q: eKeyCode.KEYCODE_Q,
    Qt.Key.Key_R: eKeyCode.KEYCODE_R,
    Qt.Key.Key_S: eKeyCode.KEYCODE_S,
    Qt.Key.Key_T: eKeyCode.KEYCODE_T,
    Qt.Key.Key_U: eKeyCode.KEYCODE_U,
    Qt.Key.Key_V: eKeyCode.KEYCODE_V,
    Qt.Key.Key_W: eKeyCode.KEYCODE_W,
    Qt.Key.Key_X: eKeyCode.KEYCODE_X,
    Qt.Key.Key_Y: eKeyCode.KEYCODE_Y,
    Qt.Key.Key_Z: eKeyCode.KEYCODE_Z,
    Qt.Key.Key_Space: eKeyCode.KEYCODE_SPACE,
    Qt.Key.Key_Return: eKeyCode.KEYCODE_ENTER,
    Qt.Key.Key_Enter: eKeyCode.KEYCODE_ENTER,
    Qt.Key.Key_Backspace: eKeyCode.KEYCODE_DEL,
    Qt.Key.Key_Delete: eKeyCode.KEYCODE_FORWARD_DEL,
    Qt.Key.Key_Tab: eKeyCode.KEYCODE_TAB,
    Qt.Key.Key_Escape: eKeyCode.KEYCODE_ESCAPE,
    Qt.Key.Key_Up: eKeyCode.KEYCODE_DPAD_UP,
    Qt.Key.Key_Down: eKeyCode.KEYCODE_DPAD_DOWN,
    Qt.Key.Key_Left: eKeyCode.KEYCODE_DPAD_LEFT,
    Qt.Key.Key_Right: eKeyCode.KEYCODE_DPAD_RIGHT,
    Qt.Key.Key_Home: eKeyCode.KEYCODE_MOVE_HOME,
    Qt.Key.Key_End: eKeyCode.KEYCODE_MOVE_END,
    Qt.Key.Key_PageUp: eKeyCode.KEYCODE_PAGE_UP,
    Qt.Key.Key_PageDown: eKeyCode.KEYCODE_PAGE_DOWN,
    Qt.Key.Key_Insert: eKeyCode.KEYCODE_INSERT,
    Qt.Key.Key_Comma: eKeyCode.KEYCODE_COMMA,
    Qt.Key.Key_Period: eKeyCode.KEYCODE_PERIOD,
    Qt.Key.Key_Slash: eKeyCode.KEYCODE_SLASH,
    Qt.Key.Key_Backslash: eKeyCode.KEYCODE_BACKSLASH,
    Qt.Key.Key_Semicolon: eKeyCode.KEYCODE_SEMICOLON,
    Qt.Key.Key_Apostrophe: eKeyCode.KEYCODE_APOSTROPHE,
    Qt.Key.Key_Minus: eKeyCode.KEYCODE_MINUS,
    Qt.Key.Key_Equal: eKeyCode.KEYCODE_EQUALS,
    Qt.Key.Key_BracketLeft: eKeyCode.KEYCODE_LEFT_BRACKET,
    Qt.Key.Key_BracketRight: eKeyCode.KEYCODE_RIGHT_BRACKET,
    Qt.Key.Key_F1: eKeyCode.KEYCODE_F1,
    Qt.Key.Key_F2: eKeyCode.KEYCODE_F2,
    Qt.Key.Key_F3: eKeyCode.KEYCODE_F3,
    Qt.Key.Key_F4: eKeyCode.KEYCODE_F4,
    Qt.Key.Key_F5: eKeyCode.KEYCODE_F5,
    Qt.Key.Key_F6: eKeyCode.KEYCODE_F6,
    Qt.Key.Key_F7: eKeyCode.KEYCODE_F7,
    Qt.Key.Key_F8: eKeyCode.KEYCODE_F8,
    Qt.Key.Key_F9: eKeyCode.KEYCODE_F9,
    Qt.Key.Key_F10: eKeyCode.KEYCODE_F10,
    Qt.Key.Key_F11: eKeyCode.KEYCODE_F11,
    Qt.Key.Key_F12: eKeyCode.KEYCODE_F12,
    Qt.Key.Key_VolumeUp: eKeyCode.KEYCODE_VOLUME_UP,
    Qt.Key.Key_VolumeDown: eKeyCode.KEYCODE_VOLUME_DOWN,
    Qt.Key.Key_VolumeMute: eKeyCode.KEYCODE_VOLUME_MUTE,
    # Device navigation shortcuts from host keyboard
    Qt.Key.Key_Back: eKeyCode.KEYCODE_BACK,
    Qt.Key.Key_Menu: eKeyCode.KEYCODE_MENU,
}


# ==================================================================================
class imageStreamer(Image):
    """Image widget that consumes scrcpy frames and injects touch/key control."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._decoder: Optional[VideoCodecContext] = None
        self._controlSocket: Optional[iControlSocket] = None
        self._hasFrame: bool = False
        self._deviceWidth: int = 0
        self._deviceHeight: int = 0
        self._captureInput: bool = True
        self._fitOnResize: bool = True
        self._touchDown: bool = False

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

    @property
    def FitOnResize(self) -> bool:
        """When True, refit the stream to the widget on every resize (MainWindow included)."""
        return self._fitOnResize

    @FitOnResize.setter
    def FitOnResize(self, enabled: bool) -> None:
        self._fitOnResize = bool(enabled)

    # ==================================================================================
    def _resolution(self) -> Point:
        return Point(self._deviceWidth, self._deviceHeight)

    def _injectTouch(self, state: eKeyState, deviceX: int, deviceY: int) -> None:
        if self._controlSocket is None:
            return
        if self._deviceWidth <= 0 or self._deviceHeight <= 0:
            return
        try:
            Touch(
                state,
                deviceX,
                deviceY,
                resolution=self._resolution(),
            ).execute(self._controlSocket)
        except Exception as ex:
            error(f"[{self.__class__.__name__}] touch inject failed", ex)

    def _injectKey(self, press: bool, event: QKeyEvent) -> None:
        if self._controlSocket is None:
            return
        if event.isAutoRepeat():
            return

        lKeyCode = _C_QT_TO_ANDROID.get(event.key())
        if lKeyCode is None:
            return

        lMeta = eMetaState.NONE
        lMods = event.modifiers()
        # eMetaState values are bitflags in Android; combine when available
        try:
            lValue = 0
            if lMods & Qt.KeyboardModifier.ShiftModifier:
                lValue |= eMetaState.SHIFT_ON.value
            if lMods & Qt.KeyboardModifier.ControlModifier:
                lValue |= eMetaState.CTRL_ON.value
            if lMods & Qt.KeyboardModifier.AltModifier:
                lValue |= eMetaState.ALT_ON.value
            if lMods & Qt.KeyboardModifier.MetaModifier:
                lValue |= eMetaState.META_ON.value
            lMeta = eMetaState(lValue) if lValue else eMetaState.NONE
        except Exception:
            lMeta = eMetaState.NONE

        try:
            if press:
                InjectKeyPress(lKeyCode, metaState=lMeta).execute(self._controlSocket)
            else:
                InjectKeyRelease(lKeyCode, metaState=lMeta).execute(self._controlSocket)
        except Exception as ex:
            error(f"[{self.__class__.__name__}] key inject failed", ex)

    # ==================================================================================
    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        if self._fitOnResize and self._hasFrame and self._image is not None:
            self.resetView()
            self._requestUpdate()

    # ==================================================================================
    @Slot(object)
    def OnFrame(self, frame: iFrame) -> None:
        """Decode one scrcpy frame and paint it without resetting zoom/pan."""
        if self._decoder is None:
            return

        try:
            lDecoded: VideoFrame | None = frame.decode(self._decoder, toGPU=False)
        except InvalidDataError:
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
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if self._captureInput and self._controlSocket is not None:
            # Right-click → BACK
            if event.button() == Qt.MouseButton.RightButton:
                try:
                    InjectKeyPress(eKeyCode.KEYCODE_BACK).execute(self._controlSocket)
                    InjectKeyRelease(eKeyCode.KEYCODE_BACK).execute(self._controlSocket)
                except Exception as ex:
                    error(f"[{self.__class__.__name__}] back inject failed", ex)
                event.accept()
                return

            if event.button() == Qt.MouseButton.LeftButton:
                lPos = event.position()
                lMapped = self._mapToDevice(lPos.x(), lPos.y())
                if lMapped is not None:
                    self._onGesturePress(lMapped[0], lMapped[1], event)
                    event.accept()
                    return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if (
            self._captureInput
            and self._controlSocket is not None
            and self._touchDown
            and event.buttons() & Qt.MouseButton.LeftButton
        ):
            lPos = event.position()
            lMapped = self._mapToDevice(lPos.x(), lPos.y())
            if lMapped is not None:
                self._onGestureMove(lMapped[0], lMapped[1], event)
                event.accept()
                return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if (
            self._captureInput
            and self._controlSocket is not None
            and event.button() == Qt.MouseButton.LeftButton
        ):
            lPos = event.position()
            lMapped = self._mapToDevice(lPos.x(), lPos.y())
            if lMapped is not None:
                self._onGestureRelease(lMapped[0], lMapped[1], event)
                event.accept()
                return
            if self._touchDown:
                self._touchDown = False
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
    def _onGesturePress(self, deviceX: int, deviceY: int, event: QMouseEvent) -> None:
        self._touchDown = True
        self._injectTouch(eKeyState.DOWN, deviceX, deviceY)

    def _onGestureMove(self, deviceX: int, deviceY: int, event: QMouseEvent) -> None:
        self._injectTouch(eKeyState.MOVE, deviceX, deviceY)

    def _onGestureRelease(self, deviceX: int, deviceY: int, event: QMouseEvent) -> None:
        self._touchDown = False
        self._injectTouch(eKeyState.UP, deviceX, deviceY)

    def _onGestureScroll(self, deviceX: int, deviceY: int, event: QWheelEvent) -> None:
        if self._controlSocket is None:
            return
        if self._deviceWidth <= 0 or self._deviceHeight <= 0:
            return

        lAngle = event.angleDelta()
        # Normalize Qt wheel ticks (typically 120) to a mild scrcpy scroll unit
        lH = float(lAngle.x()) / 120.0
        lV = float(lAngle.y()) / 120.0
        if lH == 0.0 and lV == 0.0:
            return

        try:
            Scroll(
                deviceX,
                deviceY,
                hScroll=lH,
                vScroll=lV,
                resolution=self._resolution(),
            ).execute(self._controlSocket)
        except Exception as ex:
            error(f"[{self.__class__.__name__}] scroll inject failed", ex)

    def _onKeyPress(self, event: QKeyEvent) -> None:
        self._injectKey(True, event)

    def _onKeyRelease(self, event: QKeyEvent) -> None:
        self._injectKey(False, event)
