# ==================================================================================
from __future__ import annotations

# ==================================================================================
from time import monotonic
from traceback import format_exc
from typing import Any, Callable, Dict, List, Optional, Tuple

# ==================================================================================
from PySide6.QtCore import QObject, Qt, Signal, SignalInstance
from PySide6.QtGui import QImage, QKeyEvent, QMouseEvent

# ==================================================================================
from fluxCore.action.android.enums import eKeyCode, eKeyState, eMetaState
from fluxCore.action.android.gesture import Touch
from fluxCore.action.android.injectKey import InjectKeyPress, InjectKeyRelease
from fluxCore.emitters.scrcpy import SCRCPYEmitter
from fluxCore.types.geometry import Point

# ==================================================================================
from ...types.interface.recorder import eKGRecorderState, iKGRecorder
from ...UI.pages.__devicePage import DeviceFrameBridge
from ..device import (
    DEVICE_ADDED_EVENT,
    DEVICE_INITIALIZED_EVENT,
    DEVICE_REMOVED_EVENT,
    deviceManager,
)

# ==================================================================================
C_ON_FRAME = "ON_FRAME"

# Practical Qt.Key → Android eKeyCode subset (extend as needed).
_C_QT_TO_ANDROID: Dict[int, eKeyCode] = {
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
    Qt.Key.Key_Left: eKeyCode.KEYCODE_DPAD_LEFT,
    Qt.Key.Key_Right: eKeyCode.KEYCODE_DPAD_RIGHT,
    Qt.Key.Key_Up: eKeyCode.KEYCODE_DPAD_UP,
    Qt.Key.Key_Down: eKeyCode.KEYCODE_DPAD_DOWN,
    Qt.Key.Key_Home: eKeyCode.KEYCODE_MOVE_HOME,
    Qt.Key.Key_End: eKeyCode.KEYCODE_MOVE_END,
    Qt.Key.Key_PageUp: eKeyCode.KEYCODE_PAGE_UP,
    Qt.Key.Key_PageDown: eKeyCode.KEYCODE_PAGE_DOWN,
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
    Qt.Key.Key_Back: eKeyCode.KEYCODE_BACK,
    Qt.Key.Key_Menu: eKeyCode.KEYCODE_MENU,
    Qt.Key.Key_VolumeUp: eKeyCode.KEYCODE_VOLUME_UP,
    Qt.Key.Key_VolumeDown: eKeyCode.KEYCODE_VOLUME_DOWN,
}
# ==================================================================================


# ==================================================================================
class KGRecorder(QObject):
    """Key & Gesture Recorder controller.

    Always reflects capture-surface input to the selected device.
    When Recording, the same successful actions are appended to the session.
    Device selection is locked while Recording.
    """

    stateChanged: SignalInstance = Signal(object)  # eKGRecorderState
    eventsChanged: SignalInstance = Signal(object)  # list[dict]
    statusTextChanged: SignalInstance = Signal(str)

    _sigDevicesChanged: SignalInstance = Signal()

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._state: eKGRecorderState = eKGRecorderState.Idle
        self._deviceId: Optional[str] = None
        self._events: List[Dict[str, Any]] = []
        self._sessionStart: Optional[float] = None
        self._page: Any = None
        self._capture: Any = None
        self._deviceCombo: Any = None
        self._connected: bool = False
        self._deviceManager: Optional[deviceManager] = None
        self._streamSerial: Optional[str] = None
        self._frameHandler: Optional[Callable] = None
        self._bridge: Optional[DeviceFrameBridge] = None

        self._sigDevicesChanged.connect(self._refreshDeviceCombo)

    # ------------------------------------------------------------------
    # Device manager
    # ------------------------------------------------------------------
    def setDeviceManager(self, mgr: Optional[deviceManager]) -> None:
        if self._deviceManager is mgr:
            return
        old = self._deviceManager
        if old is not None:
            try:
                old.unsubscribe(DEVICE_INITIALIZED_EVENT, self._onDevicesEvent)
                old.unsubscribe(DEVICE_ADDED_EVENT, self._onDevicesEvent)
                old.unsubscribe(DEVICE_REMOVED_EVENT, self._onDevicesEvent)
            except Exception:
                pass
        self._deviceManager = mgr
        if mgr is not None:
            mgr.subscribe(DEVICE_INITIALIZED_EVENT, self._onDevicesEvent)
            mgr.subscribe(DEVICE_ADDED_EVENT, self._onDevicesEvent)
            mgr.subscribe(DEVICE_REMOVED_EVENT, self._onDevicesEvent)
            verbose("[KGRecorder] subscribed to deviceManager events")
            self._sigDevicesChanged.emit()

    def _onDevicesEvent(self, *_args: object) -> None:
        self._sigDevicesChanged.emit()

    def _setDeviceComboEnabled(self, enabled: bool) -> None:
        combo = self._deviceCombo
        if combo is None:
            return
        try:
            combo.setEnabled(enabled)
        except Exception:
            pass

    def _refreshDeviceCombo(self) -> None:
        combo = self._deviceCombo
        if combo is None:
            return
        # Do not rebuild selection while recording — device is locked.
        if self._state == eKGRecorderState.Recording:
            self._setDeviceComboEnabled(False)
            return

        mgr = self._deviceManager
        devices: List[Any] = []
        if mgr is not None and hasattr(mgr, "values"):
            devices = [d for d in list(mgr.values()) if hasattr(d, "id")]

        prev = self._deviceId
        try:
            combo.blockSignals(True)
            combo.clear()
            if not devices:
                combo.addItem("(no devices)", None)
            else:
                for device in devices:
                    serial = str(device.id)
                    caption = (getattr(device, "name", None) or "").strip() or serial
                    combo.addItem(caption, serial)
            if prev:
                idx = combo.findData(prev)
                if idx >= 0:
                    combo.setCurrentIndex(idx)
                else:
                    self._deviceId = None
                    self._detachStream()
                    combo.setCurrentIndex(0)
            elif combo.count() > 0:
                combo.setCurrentIndex(0)
                data = combo.itemData(0)
                if data is not None:
                    self._deviceId = str(data)
        except Exception as ex:
            warning(f"[KGRecorder] refreshDeviceCombo failed: {ex}")
        finally:
            try:
                combo.blockSignals(False)
            except Exception:
                pass

        self._setDeviceComboEnabled(True)

        current = None
        try:
            data = combo.currentData()
            current = str(data) if data is not None else None
        except Exception:
            pass
        if current and current != self._streamSerial:
            self._deviceId = current
            self._attachStream(current)
        elif not current:
            self._deviceId = None
            self._detachStream()

        verbose(
            f"[KGRecorder] device combo refreshed count={combo.count()} "
            f"selected={self._deviceId!r}"
        )

    # ------------------------------------------------------------------
    # Stream attachment (CaptureImage)
    # ------------------------------------------------------------------
    def _detachStream(self) -> None:
        serial = self._streamSerial
        handler = self._frameHandler
        mgr = self._deviceManager
        if serial and handler and mgr is not None:
            emitter = mgr.getEmitter(serial)
            if emitter is not None:
                try:
                    emitter.unsubscribe(C_ON_FRAME, handler)
                except Exception:
                    pass
        self._frameHandler = None
        self._streamSerial = None
        if self._bridge is not None:
            try:
                self._bridge.frameReady.disconnect()
            except Exception:
                pass

    def _attachStream(self, serial: str) -> None:
        if not serial:
            return
        if self._streamSerial == serial and self._frameHandler is not None:
            return
        self._detachStream()
        capture = self._capture
        mgr = self._deviceManager
        if capture is None or mgr is None:
            return

        async def _run() -> None:
            try:
                emitter = await mgr.ensureRunning(serial)
            except Exception as ex:
                error(f"[KGRecorder] ensureRunning failed serial={serial!r}", ex)
                error(f"[KGRecorder] traceback:\n{format_exc()}")
                return

            bridge = self._bridge
            if bridge is None:
                bridge = DeviceFrameBridge(self)
                self._bridge = bridge
            else:
                try:
                    bridge.frameReady.disconnect()
                except Exception:
                    pass

            def _apply(img: object, v: object = capture) -> None:
                try:
                    if isinstance(img, QImage):
                        v.image = img  # type: ignore[attr-defined]
                except RuntimeError:
                    pass
                except Exception as ex:
                    warning(f"[KGRecorder] applyFrame failed: {ex}")

            bridge.frameReady.connect(_apply)

            def _onFrame(frame: object) -> None:
                try:
                    if getattr(frame, "isConfig", False):
                        self._frameToQImage(frame, emitter)
                        return
                    qimg = self._frameToQImage(frame, emitter)
                    if qimg is None:
                        return
                    try:
                        bridge.frameReady.emit(qimg)
                    except RuntimeError:
                        pass
                except Exception:
                    pass

            emitter.subscribe(C_ON_FRAME, _onFrame)
            self._frameHandler = _onFrame
            self._streamSerial = serial
            verbose(f"[KGRecorder] stream attached serial={serial!r}")

        createTask(_run)

    @staticmethod
    def _frameToQImage(frame: object, emitter: SCRCPYEmitter) -> Optional[QImage]:
        try:
            decode = getattr(frame, "decode", None)
            if decode is None:
                return None
            codec = getattr(emitter, "_codecContext", None)
            if codec is None:
                return None
            vf = decode(codec, toGPU=False)
            if vf is None:
                return None
            if hasattr(vf, "to_ndarray"):
                import numpy as np

                arr = vf.to_ndarray(format="rgb24")
                if not isinstance(arr, np.ndarray):
                    return None
                h, w, _c = arr.shape
                qimg = QImage(
                    arr.data, w, h, 3 * w, QImage.Format.Format_RGB888
                )
                return qimg.copy()
            if hasattr(vf, "to_image"):
                pil = vf.to_image()
                data = pil.convert("RGB").tobytes()
                w, h = pil.size
                qimg = QImage(data, w, h, 3 * w, QImage.Format.Format_RGB888)
                return qimg.copy()
        except Exception:
            return None
        return None

    # ------------------------------------------------------------------
    # Inject helpers
    # ------------------------------------------------------------------
    def _controlSocket(self):
        serial = self._deviceId
        mgr = self._deviceManager
        if not serial or mgr is None:
            return None
        emitter = mgr.getEmitter(serial)
        if emitter is None:
            return None
        return getattr(emitter, "ControlSocket", None)

    def _deviceResolution(self) -> Optional[Point]:
        serial = self._deviceId
        mgr = self._deviceManager
        if not serial or mgr is None:
            return None
        emitter = mgr.getEmitter(serial)
        if emitter is None:
            return None
        w = int(getattr(emitter, "width", 0) or 0)
        h = int(getattr(emitter, "height", 0) or 0)
        if w <= 0 or h <= 0:
            return None
        return Point(w, h)

    def _widgetToDevice(self, widgetX: float, widgetY: float) -> Optional[Tuple[int, int, Point]]:
        """Map capture-widget coords → device pixels using Image fit transform."""
        capture = self._capture
        resolution = self._deviceResolution()
        if capture is None or resolution is None:
            return None

        pixmap = getattr(capture, "image", None)
        if pixmap is None or pixmap.isNull():
            return None

        imgW = float(pixmap.width())
        imgH = float(pixmap.height())
        if imgW <= 0 or imgH <= 0:
            return None

        zoom = float(getattr(capture, "zoom", 100.0) or 100.0)
        scale = zoom / 100.0
        if scale <= 0:
            return None

        offset = getattr(capture, "offset", None)
        ox = float(offset.x()) if offset is not None else 0.0
        oy = float(offset.y()) if offset is not None else 0.0

        # Widget → displayed image pixel space
        imgX = (widgetX - ox) / scale
        imgY = (widgetY - oy) / scale

        # Image pixel → device resolution
        devX = imgX * (float(resolution.x) / imgW)
        devY = imgY * (float(resolution.y) / imgH)

        devX = max(0.0, min(devX, float(resolution.x)))
        devY = max(0.0, min(devY, float(resolution.y)))
        return int(devX), int(devY), resolution

    def _injectPointer(self, state: eKeyState, event: QMouseEvent) -> bool:
        control = self._controlSocket()
        if control is None:
            return False
        pos = event.position()
        mapped = self._widgetToDevice(float(pos.x()), float(pos.y()))
        if mapped is None:
            warning("[KGRecorder] injectPointer: cannot map coordinates")
            return False
        x, y, resolution = mapped
        try:
            Touch(state=state, x=x, y=y, resolution=resolution).execute(control)
            return True
        except Exception as ex:
            warning(f"[KGRecorder] injectPointer failed: {ex}")
            return False

    @staticmethod
    def _metaFromQt(modifiers: Qt.KeyboardModifier) -> eMetaState:
        meta = int(eMetaState.NONE)
        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            meta |= int(eMetaState.SHIFT_ON)
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            meta |= int(eMetaState.CTRL_ON)
        if modifiers & Qt.KeyboardModifier.AltModifier:
            meta |= int(eMetaState.ALT_ON)
        if modifiers & Qt.KeyboardModifier.MetaModifier:
            meta |= int(eMetaState.META_ON)
        try:
            return eMetaState(meta)
        except ValueError:
            return eMetaState.NONE

    def _injectKey(self, down: bool, event: QKeyEvent) -> bool:
        keyCode = _C_QT_TO_ANDROID.get(int(event.key()))
        if keyCode is None:
            return False
        control = self._controlSocket()
        if control is None:
            return False
        meta = self._metaFromQt(event.modifiers())
        try:
            if down:
                InjectKeyPress(keyCode, metaState=meta).execute(control)
            else:
                InjectKeyRelease(keyCode, metaState=meta).execute(control)
            return True
        except Exception as ex:
            warning(f"[KGRecorder] injectKey failed: {ex}")
            return False

    # ------------------------------------------------------------------
    # iKGRecorder
    # ------------------------------------------------------------------
    @property
    def state(self) -> eKGRecorderState:
        return self._state

    @property
    def deviceId(self) -> Optional[str]:
        return self._deviceId

    def setDeviceId(self, deviceId: Optional[str]) -> None:
        cleaned = (deviceId or "").strip() or None
        if cleaned == self._deviceId:
            return
        if self._state == eKGRecorderState.Recording:
            warning("[KGRecorder] setDeviceId ignored while recording")
            return
        self._deviceId = cleaned
        verbose(f"[KGRecorder] deviceId={self._deviceId!r}")
        if cleaned:
            self._attachStream(cleaned)
        else:
            self._detachStream()

    def start(self) -> None:
        if self._state == eKGRecorderState.Recording:
            return
        if not self._deviceId:
            warning("[KGRecorder] start: no device selected")
            self.statusTextChanged.emit("Select a device before recording")
            return
        if self._streamSerial != self._deviceId:
            self._attachStream(self._deviceId)
        self._events.clear()
        self._sessionStart = monotonic()
        self._setState(eKGRecorderState.Recording)
        self._setDeviceComboEnabled(False)
        self._focusCapture()
        self.eventsChanged.emit(list(self._events))
        self.statusTextChanged.emit("Recording")
        verbose("[KGRecorder] start")

    def stop(self) -> None:
        if self._state != eKGRecorderState.Recording:
            return
        self._setState(eKGRecorderState.Idle)
        self._setDeviceComboEnabled(True)
        self.statusTextChanged.emit(
            f"Stopped ({len(self._events)} event(s))"
        )
        verbose(f"[KGRecorder] stop events={len(self._events)}")

    def clear(self) -> None:
        if self._state == eKGRecorderState.Recording:
            self.stop()
        self._events.clear()
        self._sessionStart = None
        self.eventsChanged.emit([])
        self.statusTextChanged.emit("Idle")
        verbose("[KGRecorder] clear")

    def save(self, name: Optional[str] = None) -> None:
        if self._state == eKGRecorderState.Recording:
            warning("[KGRecorder] save ignored while recording; stop first")
            return
        if not self._events and self._sessionStart is None:
            warning("[KGRecorder] save: nothing to save")
            self.statusTextChanged.emit("Nothing to save")
            return
        label = (name or "").strip() or "session"
        warning(
            f"[KGRecorder] save stub name={label!r} events={len(self._events)} "
            "(MP4 + event file write not yet implemented)"
        )
        self.statusTextChanged.emit(f"Save pending: {label}")

    def open(self, name: str) -> None:
        if self._state == eKGRecorderState.Recording:
            warning("[KGRecorder] open ignored while recording")
            return
        cleaned = (name or "").strip()
        if not cleaned:
            warning("[KGRecorder] open: empty name")
            return
        warning(
            f"[KGRecorder] open stub name={cleaned!r} "
            "(load not yet implemented)"
        )
        self.statusTextChanged.emit(f"Open pending: {cleaned}")

    def bindPage(self, page: Any) -> None:
        self.unbindPage()
        self._page = page
        capture = getattr(page, "_captureImage", None)
        self._capture = capture
        self._deviceCombo = getattr(page, "_deviceCombo", None)
        if capture is None:
            warning("[KGRecorder] bindPage: page has no _captureImage")
            return
        try:
            capture.keyPressed.connect(self._onKeyPressed)
            capture.keyReleased.connect(self._onKeyReleased)
            capture.mousePressed.connect(self._onMousePressed)
            capture.mouseMoved.connect(self._onMouseMoved)
            capture.mouseReleased.connect(self._onMouseReleased)
            self._connected = True
            verbose("[KGRecorder] bound to page capture Image")
        except Exception as ex:
            error("[KGRecorder] bindPage connect failed", ex)
            error(f"[KGRecorder] traceback:\n{format_exc()}")

        self._refreshDeviceCombo()
        if self._deviceId:
            self._attachStream(self._deviceId)

    def unbindPage(self) -> None:
        self._detachStream()
        capture = self._capture
        if capture is not None and self._connected:
            for sigName, slot in (
                ("keyPressed", self._onKeyPressed),
                ("keyReleased", self._onKeyReleased),
                ("mousePressed", self._onMousePressed),
                ("mouseMoved", self._onMouseMoved),
                ("mouseReleased", self._onMouseReleased),
            ):
                try:
                    getattr(capture, sigName).disconnect(slot)
                except Exception:
                    pass
        self._connected = False
        self._capture = None
        self._deviceCombo = None
        self._page = None

    # ------------------------------------------------------------------
    def _setState(self, value: eKGRecorderState) -> None:
        if value == self._state:
            return
        self._state = value
        self.stateChanged.emit(value)

    def _focusCapture(self) -> None:
        capture = self._capture
        if capture is None:
            return
        try:
            capture.setFocus()
        except Exception:
            pass

    def _relativeMs(self) -> float:
        if self._sessionStart is None:
            return 0.0
        return (monotonic() - self._sessionStart) * 1000.0

    def _appendEvent(self, entry: Dict[str, Any]) -> None:
        self._events.append(entry)
        self.eventsChanged.emit(list(self._events))

    def _maybeLogKey(self, action: str, event: QKeyEvent) -> None:
        if self._state != eKGRecorderState.Recording:
            return
        self._appendEvent(
            {
                "type": "key",
                "action": action,
                "key": int(event.key()),
                "text": event.text(),
                "modifiers": int(event.modifiers().value),
                "t": self._relativeMs(),
            }
        )

    def _maybeLogPointer(
        self, action: str, event: QMouseEvent, x: int, y: int
    ) -> None:
        if self._state != eKGRecorderState.Recording:
            return
        self._appendEvent(
            {
                "type": "pointer",
                "action": action,
                "x": float(x),
                "y": float(y),
                "button": int(event.button().value),
                "buttons": int(event.buttons().value),
                "t": self._relativeMs(),
            }
        )

    def _onKeyPressed(self, event: object) -> None:
        if not isinstance(event, QKeyEvent):
            return
        if not self._deviceId:
            return
        if self._injectKey(True, event):
            self._maybeLogKey("down", event)

    def _onKeyReleased(self, event: object) -> None:
        if not isinstance(event, QKeyEvent):
            return
        if not self._deviceId:
            return
        if self._injectKey(False, event):
            self._maybeLogKey("up", event)

    def _onMousePressed(self, event: object) -> None:
        if not isinstance(event, QMouseEvent):
            return
        if not self._deviceId:
            return
        if self._injectPointer(eKeyState.DOWN, event):
            mapped = self._widgetToDevice(
                float(event.position().x()), float(event.position().y())
            )
            if mapped is not None:
                self._maybeLogPointer("down", event, mapped[0], mapped[1])

    def _onMouseMoved(self, event: object) -> None:
        if not isinstance(event, QMouseEvent):
            return
        if not self._deviceId:
            return
        # Hover ignored — only while dragging (finger/button down).
        if event.buttons() == Qt.MouseButton.NoButton:
            return
        if self._injectPointer(eKeyState.MOVE, event):
            mapped = self._widgetToDevice(
                float(event.position().x()), float(event.position().y())
            )
            if mapped is not None:
                self._maybeLogPointer("move", event, mapped[0], mapped[1])

    def _onMouseReleased(self, event: object) -> None:
        if not isinstance(event, QMouseEvent):
            return
        if not self._deviceId:
            return
        if self._injectPointer(eKeyState.UP, event):
            mapped = self._widgetToDevice(
                float(event.position().x()), float(event.position().y())
            )
            if mapped is not None:
                self._maybeLogPointer("up", event, mapped[0], mapped[1])
