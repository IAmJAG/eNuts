# ==================================================================================
from __future__ import annotations

from time import monotonic
from traceback import format_exc
from typing import Any, Dict, List, Optional, Tuple

from PySide6.QtCore import QObject, QSettings, Qt, Signal, SignalInstance
from PySide6.QtGui import QKeyEvent, QMouseEvent

from fluxCore.action.android.enums import eKeyCode, eKeyState, eMetaState
from fluxCore.action.android.gesture import Touch
from fluxCore.action.android.injectKey import InjectKeyPress, InjectKeyRelease
from fluxCore.types.geometry import Point

from ...types.interface.recorder import eKGRecorderState, iKGRecorder
from ..device import (
    DEVICE_ADDED_EVENT,
    DEVICE_INITIALIZED_EVENT,
    DEVICE_REMOVED_EVENT,
    deviceManager,
)
from ..stream import LocalDeviceStream

# QSettings key under MainWindow / Shell.settings
C_SETTINGS_DEVICE_ID: str = "kgRecorder/deviceId"

_C_QT_TO_ANDROID: Dict[int, eKeyCode] = {
    Qt.Key.Key_0: eKeyCode.KEYCODE_0, Qt.Key.Key_1: eKeyCode.KEYCODE_1,
    Qt.Key.Key_2: eKeyCode.KEYCODE_2, Qt.Key.Key_3: eKeyCode.KEYCODE_3,
    Qt.Key.Key_4: eKeyCode.KEYCODE_4, Qt.Key.Key_5: eKeyCode.KEYCODE_5,
    Qt.Key.Key_6: eKeyCode.KEYCODE_6, Qt.Key.Key_7: eKeyCode.KEYCODE_7,
    Qt.Key.Key_8: eKeyCode.KEYCODE_8, Qt.Key.Key_9: eKeyCode.KEYCODE_9,
    Qt.Key.Key_A: eKeyCode.KEYCODE_A, Qt.Key.Key_B: eKeyCode.KEYCODE_B,
    Qt.Key.Key_C: eKeyCode.KEYCODE_C, Qt.Key.Key_D: eKeyCode.KEYCODE_D,
    Qt.Key.Key_E: eKeyCode.KEYCODE_E, Qt.Key.Key_F: eKeyCode.KEYCODE_F,
    Qt.Key.Key_G: eKeyCode.KEYCODE_G, Qt.Key.Key_H: eKeyCode.KEYCODE_H,
    Qt.Key.Key_I: eKeyCode.KEYCODE_I, Qt.Key.Key_J: eKeyCode.KEYCODE_J,
    Qt.Key.Key_K: eKeyCode.KEYCODE_K, Qt.Key.Key_L: eKeyCode.KEYCODE_L,
    Qt.Key.Key_M: eKeyCode.KEYCODE_M, Qt.Key.Key_N: eKeyCode.KEYCODE_N,
    Qt.Key.Key_O: eKeyCode.KEYCODE_O, Qt.Key.Key_P: eKeyCode.KEYCODE_P,
    Qt.Key.Key_Q: eKeyCode.KEYCODE_Q, Qt.Key.Key_R: eKeyCode.KEYCODE_R,
    Qt.Key.Key_S: eKeyCode.KEYCODE_S, Qt.Key.Key_T: eKeyCode.KEYCODE_T,
    Qt.Key.Key_U: eKeyCode.KEYCODE_U, Qt.Key.Key_V: eKeyCode.KEYCODE_V,
    Qt.Key.Key_W: eKeyCode.KEYCODE_W, Qt.Key.Key_X: eKeyCode.KEYCODE_X,
    Qt.Key.Key_Y: eKeyCode.KEYCODE_Y, Qt.Key.Key_Z: eKeyCode.KEYCODE_Z,
    Qt.Key.Key_Space: eKeyCode.KEYCODE_SPACE, Qt.Key.Key_Return: eKeyCode.KEYCODE_ENTER,
    Qt.Key.Key_Enter: eKeyCode.KEYCODE_ENTER, Qt.Key.Key_Backspace: eKeyCode.KEYCODE_DEL,
    Qt.Key.Key_Delete: eKeyCode.KEYCODE_FORWARD_DEL, Qt.Key.Key_Tab: eKeyCode.KEYCODE_TAB,
    Qt.Key.Key_Escape: eKeyCode.KEYCODE_ESCAPE, Qt.Key.Key_Left: eKeyCode.KEYCODE_DPAD_LEFT,
    Qt.Key.Key_Right: eKeyCode.KEYCODE_DPAD_RIGHT, Qt.Key.Key_Up: eKeyCode.KEYCODE_DPAD_UP,
    Qt.Key.Key_Down: eKeyCode.KEYCODE_DPAD_DOWN, Qt.Key.Key_Home: eKeyCode.KEYCODE_MOVE_HOME,
    Qt.Key.Key_End: eKeyCode.KEYCODE_MOVE_END, Qt.Key.Key_PageUp: eKeyCode.KEYCODE_PAGE_UP,
    Qt.Key.Key_PageDown: eKeyCode.KEYCODE_PAGE_DOWN, Qt.Key.Key_Comma: eKeyCode.KEYCODE_COMMA,
    Qt.Key.Key_Period: eKeyCode.KEYCODE_PERIOD, Qt.Key.Key_Slash: eKeyCode.KEYCODE_SLASH,
    Qt.Key.Key_Backslash: eKeyCode.KEYCODE_BACKSLASH, Qt.Key.Key_Semicolon: eKeyCode.KEYCODE_SEMICOLON,
    Qt.Key.Key_Apostrophe: eKeyCode.KEYCODE_APOSTROPHE, Qt.Key.Key_Minus: eKeyCode.KEYCODE_MINUS,
    Qt.Key.Key_Equal: eKeyCode.KEYCODE_EQUALS, Qt.Key.Key_BracketLeft: eKeyCode.KEYCODE_LEFT_BRACKET,
    Qt.Key.Key_BracketRight: eKeyCode.KEYCODE_RIGHT_BRACKET, Qt.Key.Key_Back: eKeyCode.KEYCODE_BACK,
    Qt.Key.Key_Menu: eKeyCode.KEYCODE_MENU, Qt.Key.Key_VolumeUp: eKeyCode.KEYCODE_VOLUME_UP,
    Qt.Key.Key_VolumeDown: eKeyCode.KEYCODE_VOLUME_DOWN,
}


class KGRecorder(QObject):
    """KG Recorder: GLImage stream via LocalDeviceStream (SW decode)."""

    stateChanged: SignalInstance = Signal(object)
    eventsChanged: SignalInstance = Signal(object)
    statusTextChanged: SignalInstance = Signal(str)
    _sigDevicesChanged: SignalInstance = Signal()

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._state: eKGRecorderState = eKGRecorderState.Idle
        self._deviceId: Optional[str] = None
        self._events: List[Dict[str, Any]] = []
        self._sessionStart: Optional[float] = None
        self._page: Any = None
        self._streamView: Any = None
        self._deviceCombo: Any = None
        self._deviceManager: Optional[deviceManager] = None
        self._streamSerial: Optional[str] = None
        self._deviceStream: Optional[LocalDeviceStream] = None
        self._comboWired: bool = False
        self._sigDevicesChanged.connect(self._refreshDeviceCombo)

    def _mainWindowSettings(self) -> Optional[QSettings]:
        """Resolve QSettings from ENUTSWindow (Shell) via parent chain."""
        node: Optional[QObject] = self.parent()
        while node is not None:
            settings = getattr(node, "settings", None)
            if isinstance(settings, QSettings):
                return settings
            parentFn = getattr(node, "parent", None)
            node = parentFn() if callable(parentFn) else None
        return None

    def _loadPersistedDeviceId(self) -> Optional[str]:
        settings = self._mainWindowSettings()
        if settings is None:
            return None
        try:
            raw = settings.value(C_SETTINGS_DEVICE_ID, "")
            cleaned = str(raw or "").strip()
            return cleaned or None
        except Exception as ex:
            warning(f"[KGRecorder] load persisted deviceId failed: {ex}")
            return None

    def _persistDeviceId(self, deviceId: Optional[str]) -> None:
        settings = self._mainWindowSettings()
        if settings is None:
            return
        try:
            value = (deviceId or "").strip()
            settings.setValue(C_SETTINGS_DEVICE_ID, value)
            verbose(
                f"[KGRecorder] persisted deviceId={value!r} key={C_SETTINGS_DEVICE_ID!r}"
            )
        except Exception as ex:
            warning(f"[KGRecorder] persist deviceId failed: {ex}")

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

    def _wireDeviceCombo(self) -> None:
        combo = self._deviceCombo
        if combo is None or self._comboWired:
            return
        try:
            combo.currentIndexChanged.connect(self._onDeviceComboIndexChanged)
            self._comboWired = True
            verbose("[KGRecorder] device combo currentIndexChanged wired")
        except Exception as ex:
            warning(f"[KGRecorder] wire device combo failed: {ex}")

    def _unwireDeviceCombo(self) -> None:
        combo = self._deviceCombo
        if combo is None or not self._comboWired:
            self._comboWired = False
            return
        try:
            combo.currentIndexChanged.disconnect(self._onDeviceComboIndexChanged)
        except Exception:
            pass
        self._comboWired = False

    def _onDeviceComboIndexChanged(self, index: int) -> None:
        if self._state == eKGRecorderState.Recording:
            return
        combo = self._deviceCombo
        if combo is None:
            return
        try:
            data = combo.itemData(index) if index >= 0 else None
        except Exception:
            data = None
        serial = str(data).strip() if data is not None else None
        if not serial:
            serial = None
        if serial == self._deviceId:
            return
        self._deviceId = serial
        self._persistDeviceId(serial)
        if serial:
            self._attachStream(serial)
        else:
            self._detachStream()
        verbose(f"[KGRecorder] combo selected deviceId={serial!r}")

    def _refreshDeviceCombo(self) -> None:
        combo = self._deviceCombo
        if combo is None:
            return
        if self._state == eKGRecorderState.Recording:
            self._setDeviceComboEnabled(False)
            return

        mgr = self._deviceManager
        devices: List[Any] = []
        if mgr is not None and hasattr(mgr, "values"):
            devices = [d for d in list(mgr.values()) if hasattr(d, "id")]

        preferred = self._deviceId or self._loadPersistedDeviceId()

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

            chosen: Optional[str] = None
            if preferred:
                idx = combo.findData(preferred)
                if idx >= 0:
                    combo.setCurrentIndex(idx)
                    chosen = preferred
                elif devices:
                    combo.setCurrentIndex(0)
                    data = combo.itemData(0)
                    chosen = str(data) if data is not None else None
                else:
                    combo.setCurrentIndex(0)
                    chosen = None
            elif combo.count() > 0:
                combo.setCurrentIndex(0)
                data = combo.itemData(0)
                chosen = str(data) if data is not None else None

            self._deviceId = chosen
        except Exception as ex:
            warning(f"[KGRecorder] refreshDeviceCombo failed: {ex}")
        finally:
            try:
                combo.blockSignals(False)
            except Exception:
                pass

        self._setDeviceComboEnabled(True)

        if self._deviceId and self._deviceId != self._streamSerial:
            self._attachStream(self._deviceId)
        elif not self._deviceId:
            self._detachStream()

    def _detachStream(self) -> None:
        stream = self._deviceStream
        if stream is not None:
            try:
                stream.stop()
            except Exception:
                pass
        self._deviceStream = None
        self._streamSerial = None

    def _attachStream(self, serial: str) -> None:
        if not serial:
            return
        if self._streamSerial == serial and self._deviceStream is not None:
            return
        self._detachStream()
        view = self._streamView
        mgr = self._deviceManager
        if view is None or mgr is None:
            warning("[KGRecorder] attachStream: missing streamView or deviceManager")
            return

        async def _run() -> None:
            try:
                stream = LocalDeviceStream(mgr, parent=self)
                stream.attachView(view)
                await stream.ensureRunning(serial)
                self._deviceStream = stream
                self._streamSerial = serial
                verbose(f"[KGRecorder] stream attached serial={serial!r} via LocalDeviceStream")
            except Exception as ex:
                error(f"[KGRecorder] ensureRunning failed serial={serial!r}", ex)
                error(f"[KGRecorder] traceback:\n{format_exc()}")

        createTask(_run)

    def _flushStreamView(self) -> None:
        view = self._streamView
        if view is None:
            return
        try:
            if hasattr(view, "clearPresent"):
                view.clearPresent()
            elif hasattr(view, "image"):
                view.image = None
        except Exception as ex:
            warning(f"[KGRecorder] flushStreamView failed: {ex}")

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
        view = self._streamView
        resolution = self._deviceResolution()
        if view is None or resolution is None:
            return None
        imgW = float(getattr(view, "_contentW", 0) or 0)
        imgH = float(getattr(view, "_contentH", 0) or 0)
        if imgW <= 0 or imgH <= 0:
            pixmap = getattr(view, "image", None)
            if pixmap is None or getattr(pixmap, "isNull", lambda: True)():
                return None
            imgW = float(pixmap.width())
            imgH = float(pixmap.height())
        if imgW <= 0 or imgH <= 0:
            return None
        vw = float(view.width()) if hasattr(view, "width") else imgW
        vh = float(view.height()) if hasattr(view, "height") else imgH
        if vw <= 0 or vh <= 0:
            return None
        scale = min(vw / imgW, vh / imgH)
        tw, th = imgW * scale, imgH * scale
        ox, oy = (vw - tw) / 2.0, (vh - th) / 2.0
        imgX = (widgetX - ox) / scale
        imgY = (widgetY - oy) / scale
        devX = max(0.0, min(imgX * (float(resolution.x) / imgW), float(resolution.x)))
        devY = max(0.0, min(imgY * (float(resolution.y) / imgH), float(resolution.y)))
        return int(devX), int(devY), resolution

    def _injectPointer(self, state: eKeyState, event: QMouseEvent) -> bool:
        control = self._controlSocket()
        if control is None:
            return False
        pos = event.position()
        mapped = self._widgetToDevice(float(pos.x()), float(pos.y()))
        if mapped is None:
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
        self._persistDeviceId(cleaned)
        combo = self._deviceCombo
        if combo is not None:
            try:
                combo.blockSignals(True)
                if cleaned:
                    idx = combo.findData(cleaned)
                    if idx >= 0:
                        combo.setCurrentIndex(idx)
                else:
                    combo.setCurrentIndex(0)
            except Exception:
                pass
            finally:
                try:
                    combo.blockSignals(False)
                except Exception:
                    pass
        if cleaned:
            self._attachStream(cleaned)
        else:
            self._detachStream()

    def start(self) -> None:
        if self._state == eKGRecorderState.Recording:
            return
        if not self._deviceId:
            warning("[KGRecorder] start: no device selected")
            return
        mgr = self._deviceManager
        if mgr is not None:
            try:
                mgr.stopExcept(self._deviceId)
            except Exception as ex:
                warning(f"[KGRecorder] stopExcept on start failed: {ex}")
        self._flushStreamView()
        self._events = []
        self._sessionStart = monotonic()
        self.eventsChanged.emit([])
        self._attachStream(self._deviceId)
        self._setState(eKGRecorderState.Recording)
        self._setDeviceComboEnabled(False)
        self.statusTextChanged.emit("Recording")

    def stop(self) -> None:
        if self._state != eKGRecorderState.Recording:
            return
        self._setState(eKGRecorderState.Idle)
        self._setDeviceComboEnabled(True)
        self._sessionStart = None
        self.statusTextChanged.emit(f"Stopped ({len(self._events)} events)")

    def clear(self) -> None:
        if self._state == eKGRecorderState.Recording:
            self.stop()
        self._events = []
        self.eventsChanged.emit([])

    def save(self, path: Optional[str] = None) -> None:
        if self._state == eKGRecorderState.Recording:
            return
        if not self._events:
            return
        cleaned = (path or "").strip()
        if cleaned:
            warning(f"[KGRecorder] save stub path={cleaned!r}")

    def open(self, path: Optional[str] = None) -> None:
        cleaned = (path or "").strip()
        if cleaned:
            warning(f"[KGRecorder] open stub name={cleaned!r}")

    def _wireStreamInput(self, view: Any) -> None:
        """Connect CaptureGLImage / CaptureImage input signals to inject/log slots."""
        if view is None:
            return
        pairs = (
            ("keyPressed", self._onKeyPressed),
            ("keyReleased", self._onKeyReleased),
            ("mousePressed", self._onMousePressed),
            ("mouseMoved", self._onMouseMoved),
            ("mouseReleased", self._onMouseReleased),
        )
        for name, slot in pairs:
            sig = getattr(view, name, None)
            if sig is None:
                continue
            try:
                sig.connect(slot)
            except Exception as ex:
                warning(f"[KGRecorder] connect {name} failed: {ex}")

    def _unwireStreamInput(self, view: Any) -> None:
        if view is None:
            return
        pairs = (
            ("keyPressed", self._onKeyPressed),
            ("keyReleased", self._onKeyReleased),
            ("mousePressed", self._onMousePressed),
            ("mouseMoved", self._onMouseMoved),
            ("mouseReleased", self._onMouseReleased),
        )
        for name, slot in pairs:
            sig = getattr(view, name, None)
            if sig is None:
                continue
            try:
                sig.disconnect(slot)
            except Exception:
                pass

    def bindPage(self, page: Any) -> None:
        self.unbindPage()
        self._page = page
        view = getattr(page, "_streamView", None)
        self._streamView = view
        self._deviceCombo = getattr(page, "_deviceCombo", None)
        if view is None:
            warning("[KGRecorder] bindPage: page has no _streamView (CaptureGLImage)")
            return
        verbose(f"[KGRecorder] bound to page streamView={type(view).__name__}")

        self._wireStreamInput(view)

        if not self._deviceId:
            self._deviceId = self._loadPersistedDeviceId()

        self._wireDeviceCombo()
        self._refreshDeviceCombo()
        if self._deviceId:
            self._attachStream(self._deviceId)

    def unbindPage(self) -> None:
        self._unwireStreamInput(self._streamView)
        self._unwireDeviceCombo()
        self._detachStream()
        self._streamView = None
        self._deviceCombo = None
        self._page = None

    def _setState(self, value: eKGRecorderState) -> None:
        if value == self._state:
            return
        self._state = value
        self.stateChanged.emit(value)

    def _focusCapture(self) -> None:
        view = self._streamView
        if view is None:
            return
        try:
            view.setFocus()
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
        self._appendEvent({"t": self._relativeMs(), "type": "key", "action": action, "key": int(event.key())})

    def _maybeLogPointer(self, action: str, event: QMouseEvent) -> None:
        if self._state != eKGRecorderState.Recording:
            return
        pos = event.position()
        self._appendEvent({"t": self._relativeMs(), "type": "pointer", "action": action, "x": float(pos.x()), "y": float(pos.y())})

    def _onKeyPressed(self, event: QKeyEvent) -> None:
        if self._injectKey(True, event):
            self._maybeLogKey("down", event)

    def _onKeyReleased(self, event: QKeyEvent) -> None:
        if self._injectKey(False, event):
            self._maybeLogKey("up", event)

    def _onMousePressed(self, event: QMouseEvent) -> None:
        if self._injectPointer(eKeyState.DOWN, event):
            self._maybeLogPointer("down", event)

    def _onMouseMoved(self, event: QMouseEvent) -> None:
        if int(event.buttons()) == 0:
            return
        if self._injectPointer(eKeyState.MOVE, event):
            self._maybeLogPointer("move", event)

    def _onMouseReleased(self, event: QMouseEvent) -> None:
        if self._injectPointer(eKeyState.UP, event):
            self._maybeLogPointer("up", event)
