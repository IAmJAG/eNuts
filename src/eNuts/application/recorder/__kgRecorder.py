# ==================================================================================
from __future__ import annotations

# ==================================================================================
from time import monotonic
from traceback import format_exc
from typing import Any, Callable, Dict, List, Optional

# ==================================================================================
from PySide6.QtCore import QObject, Signal, SignalInstance
from PySide6.QtGui import QImage, QKeyEvent, QMouseEvent

# ==================================================================================
from fluxCore.emitters.scrcpy import SCRCPYEmitter

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
# ==================================================================================


# ==================================================================================
class KGRecorder(QObject):
    """Key & Gesture Recorder controller.

    Component of ENUTSWindow; wired from Shell. Owns session state,
    event collection, device-combo population, stream attachment to
    CaptureImage, and (later) paired MP4 + event-file persistence.
    The Page is a pure view.
    """

    stateChanged: SignalInstance = Signal(object)  # eKGRecorderState
    eventsChanged: SignalInstance = Signal(object)  # list[dict]
    statusTextChanged: SignalInstance = Signal(str)

    # Cross-thread device-list updates (deviceManager callbacks are async)
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

    def _refreshDeviceCombo(self) -> None:
        combo = self._deviceCombo
        if combo is None:
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
            # Restore previous selection when still present
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

        # Ensure stream matches current selection
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
        # Ensure stream is live before recording
        if self._streamSerial != self._deviceId:
            self._attachStream(self._deviceId)
        self._events.clear()
        self._sessionStart = monotonic()
        self._setState(eKGRecorderState.Recording)
        self._focusCapture()
        self.eventsChanged.emit(list(self._events))
        self.statusTextChanged.emit("Recording")
        verbose("[KGRecorder] start")

    def stop(self) -> None:
        if self._state != eKGRecorderState.Recording:
            return
        self._setState(eKGRecorderState.Idle)
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
        """Persist paired MP4 + event file.

        File naming / directory convention depends on intent and is deferred.
        Continuous video + event stream must remain aligned.
        """
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
        """Load a previously saved paired recording.

        Naming convention deferred with save().
        """
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

    def _onKeyPressed(self, event: object) -> None:
        if self._state != eKGRecorderState.Recording:
            return
        if not isinstance(event, QKeyEvent):
            return
        self._appendEvent(
            {
                "type": "key",
                "action": "down",
                "key": int(event.key()),
                "text": event.text(),
                "modifiers": int(event.modifiers().value),
                "t": self._relativeMs(),
            }
        )

    def _onKeyReleased(self, event: object) -> None:
        if self._state != eKGRecorderState.Recording:
            return
        if not isinstance(event, QKeyEvent):
            return
        self._appendEvent(
            {
                "type": "key",
                "action": "up",
                "key": int(event.key()),
                "text": event.text(),
                "modifiers": int(event.modifiers().value),
                "t": self._relativeMs(),
            }
        )

    def _onMousePressed(self, event: object) -> None:
        if self._state != eKGRecorderState.Recording:
            return
        if not isinstance(event, QMouseEvent):
            return
        self._appendPointer("down", event)

    def _onMouseMoved(self, event: object) -> None:
        if self._state != eKGRecorderState.Recording:
            return
        if not isinstance(event, QMouseEvent):
            return
        self._appendPointer("move", event)

    def _onMouseReleased(self, event: object) -> None:
        if self._state != eKGRecorderState.Recording:
            return
        if not isinstance(event, QMouseEvent):
            return
        self._appendPointer("up", event)

    def _appendPointer(self, action: str, event: QMouseEvent) -> None:
        # Coordinates stored in widget space for now.
        # Normalization to stream resolution is deferred to recorder coding phase.
        pos = event.position()
        self._appendEvent(
            {
                "type": "pointer",
                "action": action,
                "x": float(pos.x()),
                "y": float(pos.y()),
                "button": int(event.button().value),
                "buttons": int(event.buttons().value),
                "t": self._relativeMs(),
            }
        )
