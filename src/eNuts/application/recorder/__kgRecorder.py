# ==================================================================================
from __future__ import annotations

# ==================================================================================
from time import monotonic
from traceback import format_exc
from typing import Any, Callable, Dict, List, Optional

# ==================================================================================
from PySide6.QtCore import QObject, Signal, SignalInstance
from PySide6.QtGui import QKeyEvent, QMouseEvent

# ==================================================================================
from ...types.interface.recorder import eKGRecorderState, iKGRecorder


# ==================================================================================
class KGRecorder(QObject):
    """Key & Gesture Recorder controller.

    Component of ENUTSWindow; wired from Shell. Owns session state,
    event collection, and (later) paired MP4 + event-file persistence.
    The Page is a pure view.
    """

    stateChanged: SignalInstance = Signal(object)  # eKGRecorderState
    eventsChanged: SignalInstance = Signal(object)  # list[dict]
    statusTextChanged: SignalInstance = Signal(str)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._state: eKGRecorderState = eKGRecorderState.Idle
        self._deviceId: Optional[str] = None
        self._events: List[Dict[str, Any]] = []
        self._sessionStart: Optional[float] = None
        self._page: Any = None
        self._capture: Any = None
        self._connected: bool = False

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

    def start(self) -> None:
        if self._state == eKGRecorderState.Recording:
            return
        if not self._deviceId:
            warning("[KGRecorder] start: no device selected")
            self.statusTextChanged.emit("Select a device before recording")
            return
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
        # Persistence format and path convention deferred (intent-dependent).
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

    def unbindPage(self) -> None:
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
