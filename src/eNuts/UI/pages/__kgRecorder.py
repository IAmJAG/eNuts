# ==================================================================================
from __future__ import annotations

# ==================================================================================
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import uuid4

# ==================================================================================
from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QIcon, QKeyEvent, QMouseEvent, QPixmap
from PySide6.QtWidgets import (
    QBoxLayout,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QWidget,
)

# ==================================================================================
from fluxCore.action.android.enums import eKeyCode, eKeyState
from fluxCore.action.android.gesture import Touch
from fluxCore.action.android.injectKey import InjectKeyPress, InjectKeyRelease
from fluxCore.stream import LocalDeviceStream
from fluxCore.types.geometry import Point
from fluxCore.types.interface.device import iDevice

# ==================================================================================
from ...services.device import (
    DEVICE_ADDED_EVENT,
    DEVICE_INITIALIZED_EVENT,
    DEVICE_REMOVED_EVENT,
)
from ...services.recorder import KGRecorderService
from ...types.interface.application import iShell
from ...types.interface.services.device import iDeviceManager
from ...types.interface.services.recorder import iKGRecorderService
from ..widgets import CaptureGLImage
from .__playbackBase import PlaybackBase

# ==================================================================================
C_SETTINGS_DEVICE_ID: str = "RECORDER_DEVICE_ID"
C_RECORDINGS_DIR: str = "recordings"
# ==================================================================================


# ==================================================================================
class eKGRecorderState(Enum):
    Idle = auto()
    Recording = auto()


# ==================================================================================
# Practical Qt → Android key map (subset; extend later).
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
    Qt.Key.Key_Up: eKeyCode.KEYCODE_DPAD_UP,
    Qt.Key.Key_Down: eKeyCode.KEYCODE_DPAD_DOWN,
    Qt.Key.Key_Left: eKeyCode.KEYCODE_DPAD_LEFT,
    Qt.Key.Key_Right: eKeyCode.KEYCODE_DPAD_RIGHT,
    Qt.Key.Key_Home: eKeyCode.KEYCODE_MOVE_HOME,
    Qt.Key.Key_End: eKeyCode.KEYCODE_MOVE_END,
    Qt.Key.Key_PageUp: eKeyCode.KEYCODE_PAGE_UP,
    Qt.Key.Key_PageDown: eKeyCode.KEYCODE_PAGE_DOWN,
    Qt.Key.Key_VolumeUp: eKeyCode.KEYCODE_VOLUME_UP,
    Qt.Key.Key_VolumeDown: eKeyCode.KEYCODE_VOLUME_DOWN,
    Qt.Key.Key_Back: eKeyCode.KEYCODE_BACK,
}
# ==================================================================================


# ==================================================================================
class KGRecorder(PlaybackBase):
    """KG Recorder page: device combo, stream, and recording UI controller.

    Session capture is delegated to ``KGRecorderService`` (every emitter frame +
    key/pointer events). This page owns Idle|Recording UI state, inject, and
    ``LocalDeviceStream`` preview via ``switchDevice``.
    """

    def __init__(
        self,
        title: str,
        description: str = "",
        icon: Optional[Union[QIcon, QPixmap, str]] = None,
        commandBarOn: bool = True,
        id: Optional[str] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(
            title=title,
            description=description,
            icon=icon,
            commandBarOn=commandBarOn,
            id=id,
            *args,
            **kwargs,
        )
        self._stream: LocalDeviceStream = LocalDeviceStream(ringSize=8)
        self._state: eKGRecorderState = eKGRecorderState.Idle
        self._recorder: iKGRecorderService = KGRecorderService()
        self._lastSessionResult: Optional[Dict[str, Any]] = None
        self._captureWired: bool = False

    @classmethod
    def classname(cls) -> str:
        return cls.__name__

    # -------------------------------------------------------------------------
    # session
    # -------------------------------------------------------------------------
    @property
    def state(self) -> eKGRecorderState:
        return self._state

    @property
    def events(self) -> List[Dict[str, Any]]:
        return self._recorder.events

    @property
    def recorder(self) -> iKGRecorderService:
        return self._recorder

    def start(self) -> None:
        if self._state is eKGRecorderState.Recording:
            return
        serial = self._stream._serial
        if not serial:
            warning(f"[{self.classname()}] start blocked: no device selected")
            return

        mgr = self.deviceManager
        emitter = mgr.get(serial) if mgr is not None else None
        if emitter is None:
            warning(
                f"[{self.classname()}] start blocked: no emitter for serial={serial!r}"
            )
            return

        width = int(getattr(emitter, "width", 0) or 0)
        height = int(getattr(emitter, "height", 0) or 0)
        codec = str(getattr(emitter, "codecId", None) or "h264")

        sessionDir = self._sessionDirPath(None)
        try:
            self._recorder.bind(
                emitter,
                serial=str(serial),
                width=width,
                height=height,
                codec=codec,
            )
            self._recorder.start(sessionDir)
        except Exception as ex:
            error(f"[{self.classname()}] recorder start failed: {ex}")
            return

        self._state = eKGRecorderState.Recording
        self._lastSessionResult = None
        self._setDeviceComboEnabled(False)
        verbose(
            f"[{self.classname()}] recording started serial={serial!r} "
            f"dir={str(sessionDir)!r}"
        )

    def stop(self) -> None:
        if self._state is not eKGRecorderState.Recording:
            return
        try:
            self._lastSessionResult = self._recorder.stop()
        except Exception as ex:
            error(f"[{self.classname()}] recorder stop failed: {ex}")
            self._lastSessionResult = None
        self._state = eKGRecorderState.Idle
        self._setDeviceComboEnabled(True)
        result = self._lastSessionResult or {}
        verbose(
            f"[{self.classname()}] recording stopped "
            f"frames={result.get('frameCount', 0)} "
            f"events={len(result.get('events', []))} "
            f"dir={result.get('sessionDir')!r}"
        )

    def clear(self) -> None:
        self._recorder.clearEvents()
        verbose(f"[{self.classname()}] session events cleared")

    def save(self, name: Optional[str] = None) -> None:
        # Finalize current session if still recording; artefacts already on disk.
        if self._state is eKGRecorderState.Recording:
            self.stop()
        result = self._lastSessionResult
        if result is None:
            warning(f"[{self.classname()}] save: no session result name={name!r}")
            return
        verbose(
            f"[{self.classname()}] save name={name!r} "
            f"video={result.get('videoPath')!r} "
            f"manifest={result.get('manifestPath')!r} "
            f"frames={result.get('frameCount', 0)} "
            f"events={len(result.get('events', []))}"
        )

    def open(self, name: Optional[str] = None) -> None:
        # Deferred: load paired artefacts.
        warning(f"[{self.classname()}] open deferred name={name!r}")

    def _sessionDirPath(self, name: Optional[str] = None) -> Path:
        stem = (name or "").strip() or uuid4().hex
        root = Path.cwd() / C_RECORDINGS_DIR
        return root / stem

    def _logEvent(self, kind: str, payload: Dict[str, Any]) -> None:
        if self._state is not eKGRecorderState.Recording:
            return
        if kind == "key":
            self._recorder.logKey(
                str(payload.get("action", "")),
                str(payload.get("key", "")),
            )
        elif kind == "pointer":
            self._recorder.logPointer(
                str(payload.get("action", "")),
                int(payload.get("x", 0)),
                int(payload.get("y", 0)),
            )

    # -------------------------------------------------------------------------
    # device combo / stream
    # -------------------------------------------------------------------------
    def _setDeviceComboEnabled(self, enabled: bool) -> None:
        combo = getattr(self, "_deviceCombo", None)
        if combo is None:
            return
        try:
            combo.setEnabled(enabled)
        except Exception:
            pass

    def _refreshDeviceCombo(self, *args, **kwargs) -> None:
        if self._state is eKGRecorderState.Recording:
            return
        try:
            deviceCombo: QComboBox = self._deviceCombo
            self.blockWidgetSignals(deviceCombo)

            deviceCombo.clear()
            devices: List[iDevice] = [d for d in list(self.deviceManager.values())]

            if len(devices) == 0 or not devices:
                deviceCombo.placeholderText = "<No Device Found>"
            else:
                deviceCombo.placeholderText = "<Select Device>"
                for device in devices:
                    name: str = device.name.strip().lower()
                    deviceCombo.addItem(name, device.id)

            deviceId = self.settings.value(C_SETTINGS_DEVICE_ID, EMPTY)
            idx = deviceCombo.findData(deviceId)
            if idx >= 0:
                deviceCombo.setCurrentIndex(idx)
            elif deviceCombo.count() > 0:
                deviceCombo.setCurrentIndex(0)
                deviceId = deviceCombo.itemData(0)

            self._setDevice(deviceId)

        except Exception as ex:
            warning(f"refresh device combo failed: {ex}")

        finally:
            self.restoreWidgetSignals(deviceCombo)

    def _setDevice(self, deviceId: Optional[str]) -> None:
        if self._state is eKGRecorderState.Recording:
            warning(f"[{self.classname()}] setDevice blocked while Recording")
            return
        cleaned: Optional[str] = (str(deviceId).strip() if deviceId else "") or None
        self._persistDeviceId(cleaned)
        verbose(f"[{self.classname()}] setting deviceId={cleaned!r}")
        createTask(self._stream.switchDevice, self.deviceManager, cleaned)

    def _persistDeviceId(self, deviceId: Optional[str]) -> None:
        settings: QSettings = self.settings
        if settings is None:
            return
        try:
            value = (deviceId or "").strip()
            settings.setValue(C_SETTINGS_DEVICE_ID, value)
            verbose(f"persisted deviceId={value!r} key={C_SETTINGS_DEVICE_ID!r}")
        except Exception as ex:
            warning(f"persist deviceId failed: {ex}")

    def _wInitializeServices(self) -> None:
        super()._wInitializeServices()

    def _wBindComponents(self) -> None:
        super()._wBindComponents()
        cboDevices: QComboBox = self._deviceCombo
        cboDevices.currentTextChanged.connect(self._onDeviceChanged)

        deviceMngr: iDeviceManager = self.deviceManager
        deviceMngr.subscribe(DEVICE_INITIALIZED_EVENT, self._refreshDeviceCombo)
        deviceMngr.subscribe(DEVICE_ADDED_EVENT, self._onDeviceAdded)
        deviceMngr.subscribe(DEVICE_REMOVED_EVENT, self._onDeviceRemoved)

        self._wireCaptureSignals()

    def _onDeviceChanged(self, device: str, *args, **kwargs) -> None:
        if self._state is eKGRecorderState.Recording:
            return
        cboDevices: QComboBox = self._deviceCombo
        deviceId = cboDevices.itemData(cboDevices.findText(device))
        self._setDevice(deviceId)

    def _onDeviceAdded(self, device: iDevice, *args, **kwargs) -> None:
        if self._state is eKGRecorderState.Recording:
            return
        cboDevices: QComboBox = self._deviceCombo
        deviceId: str = device.id
        newIndex: int = cboDevices.findData(deviceId)
        if newIndex == -1:
            deviceName: str = device.name.strip().lower()
            cboDevices.addItem(deviceName, deviceId)
            verbose(f"added device={deviceId!r}:{deviceName!r}")

    def _onDeviceRemoved(self, device: iDevice, *args, **kwargs) -> None:
        cboDevices: QComboBox = self._deviceCombo
        deviceId: str = device.id
        index: int = cboDevices.findData(deviceId)
        if index != -1:
            cboDevices.removeItem(index)
            deviceName: str = device.name.strip().lower()
            verbose(f"removed device={deviceId!r}:{deviceName!r}")
            if self._stream._serial == deviceId:
                if self._state is eKGRecorderState.Recording:
                    self.stop()
                self._setDevice(None)

    # -------------------------------------------------------------------------
    # CaptureGLImage → inject + log
    # -------------------------------------------------------------------------
    def _wireCaptureSignals(self) -> None:
        view = getattr(self, "_streamView", None)
        if view is None or self._captureWired:
            return
        if not isinstance(view, CaptureGLImage):
            warning(
                f"[{self.classname()}] streamView is not CaptureGLImage; "
                f"input signals not wired"
            )
            return
        try:
            view.keyPressed.connect(self._onKeyPressed)
            view.keyReleased.connect(self._onKeyReleased)
            view.mousePressed.connect(self._onMousePressed)
            view.mouseMoved.connect(self._onMouseMoved)
            view.mouseReleased.connect(self._onMouseReleased)
            self._captureWired = True
            verbose(f"[{self.classname()}] CaptureGLImage signals wired")
        except Exception as ex:
            warning(f"[{self.classname()}] wire capture signals failed: {ex}")

    def _controlSocket(self) -> Any:
        serial = self._stream._serial
        if not serial:
            return None
        mgr = self.deviceManager
        if mgr is None:
            return None
        emitter = mgr.get(serial)
        if emitter is None:
            return None
        return getattr(emitter, "ControlSocket", None)

    def _deviceResolution(self) -> Point:
        serial = self._stream._serial
        if serial:
            emitter = self.deviceManager.get(serial) if self.deviceManager else None
            if emitter is not None:
                w = int(getattr(emitter, "width", 0) or 0)
                h = int(getattr(emitter, "height", 0) or 0)
                if w > 0 and h > 0:
                    return Point(w, h)
        view = getattr(self, "_streamView", None)
        if view is not None and hasattr(view, "contentSize"):
            cw, ch = view.contentSize()
            if cw > 0 and ch > 0:
                return Point(cw, ch)
        if view is not None:
            return Point(max(1, view.width()), max(1, view.height()))
        return Point(1080, 1920)

    def _widgetToDevice(self, event: QMouseEvent) -> Optional[Tuple[int, int]]:
        """Widget → image-fit content → device resolution.

        Uses ``GLImage.mapToContent`` (same Scale/Fill/Crop math as paint).
        Returns ``None`` when the point is outside the fitted image (Scale bars)
        or content is not available yet.
        """
        view = self._streamView
        if view is None:
            return None

        pos = event.position()
        mapped: Optional[Tuple[float, float]] = None
        if hasattr(view, "mapToContent"):
            mapped = view.mapToContent(float(pos.x()), float(pos.y()))
        if mapped is None:
            return None

        cx, cy = mapped
        res = self._deviceResolution()
        contentW, contentH = 0, 0
        if hasattr(view, "contentSize"):
            contentW, contentH = view.contentSize()

        if contentW > 0 and contentH > 0 and (
            contentW != int(res.x) or contentH != int(res.y)
        ):
            x = int(cx * (res.x / contentW))
            y = int(cy * (res.y / contentH))
        else:
            x = int(cx)
            y = int(cy)

        x = max(0, min(int(res.x), x))
        y = max(0, min(int(res.y), y))
        return x, y

    def _onKeyPressed(self, event: QKeyEvent) -> None:
        code = _C_QT_TO_ANDROID.get(int(event.key()))
        if code is None:
            return
        control = self._controlSocket()
        if control is None:
            return
        try:
            InjectKeyPress(code).execute(control)
            self._logEvent("key", {"action": "down", "key": code.name})
        except Exception as ex:
            warning(f"[{self.classname()}] inject key press failed: {ex}")

    def _onKeyReleased(self, event: QKeyEvent) -> None:
        code = _C_QT_TO_ANDROID.get(int(event.key()))
        if code is None:
            return
        control = self._controlSocket()
        if control is None:
            return
        try:
            InjectKeyRelease(code).execute(control)
            self._logEvent("key", {"action": "up", "key": code.name})
        except Exception as ex:
            warning(f"[{self.classname()}] inject key release failed: {ex}")

    def _onMousePressed(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return
        control = self._controlSocket()
        if control is None:
            return
        mapped = self._widgetToDevice(event)
        if mapped is None:
            return
        x, y = mapped
        res = self._deviceResolution()
        try:
            Touch(eKeyState.DOWN, x, y, resolution=res).execute(control)
            self._logEvent("pointer", {"action": "down", "x": x, "y": y})
        except Exception as ex:
            warning(f"[{self.classname()}] inject touch down failed: {ex}")

    def _onMouseMoved(self, event: QMouseEvent) -> None:
        # Pointer move only while dragging.
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        control = self._controlSocket()
        if control is None:
            return
        mapped = self._widgetToDevice(event)
        if mapped is None:
            return
        x, y = mapped
        res = self._deviceResolution()
        try:
            Touch(eKeyState.MOVE, x, y, resolution=res).execute(control)
            self._logEvent("pointer", {"action": "move", "x": x, "y": y})
        except Exception as ex:
            warning(f"[{self.classname()}] inject touch move failed: {ex}")

    def _onMouseReleased(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return
        control = self._controlSocket()
        if control is None:
            return
        mapped = self._widgetToDevice(event)
        if mapped is None:
            return
        x, y = mapped
        res = self._deviceResolution()
        try:
            Touch(eKeyState.UP, x, y, resolution=res).execute(control)
            self._logEvent("pointer", {"action": "up", "x": x, "y": y})
        except Exception as ex:
            warning(f"[{self.classname()}] inject touch up failed: {ex}")

    def _wInitializeUI(self) -> None:
        super()._wInitializeUI(CaptureGLImage)

        view: CaptureGLImage = self._streamView
        self._stream.attachView(view)

        layout: QBoxLayout = self.Layout
        layout.setDirection(QBoxLayout.Direction.LeftToRight)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        utils: QWidget = QWidget()
        utils.setObjectName(f"{self.OBJECT_NAME}_UTILS")
        utils.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        utils.setFixedWidth(280)

        utilsLayout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        utilsLayout.setContentsMargins(8, 8, 8, 8)
        utilsLayout.setSpacing(8)

        deviceRow = QHBoxLayout()
        deviceRow.setSpacing(6)
        deviceLabel = QLabel("Device")
        deviceLabel.setObjectName(f"{self.OBJECT_NAME}_DEVICE_LABEL")
        deviceCombo = QComboBox()
        deviceCombo.setObjectName(f"{self.OBJECT_NAME}_DEVICE_COMBO")
        deviceCombo.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        deviceRow.addWidget(deviceLabel)
        deviceRow.addWidget(deviceCombo, 1)
        utilsLayout.addLayout(deviceRow)
        utilsLayout.addStretch(1)
        utils.setLayout(utilsLayout)

        layout.addWidget(utils)

        self._deviceCombo = deviceCombo
        self._utilsPanel = utils

    @property
    def shell(self) -> iShell:
        return self.Parent.Parent

    @property
    def settings(self) -> QSettings:
        return self.shell.settings

    @property
    def deviceManager(self) -> iDeviceManager:
        return self.shell.deviceManager
