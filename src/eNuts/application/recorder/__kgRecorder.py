# ==================================================================================
from __future__ import annotations

from traceback import format_exc
from typing import Any, List, Optional

from PySide6.QtCore import QObject, QSettings, Signal, SignalInstance

from ..device import (
    DEVICE_ADDED_EVENT,
    DEVICE_INITIALIZED_EVENT,
    DEVICE_REMOVED_EVENT,
    deviceManager,
)
from ..stream import LocalDeviceStream

# QSettings key under MainWindow / Shell.settings
C_SETTINGS_DEVICE_ID: str = "kgRecorder/deviceId"


class KGRecorder(QObject):
    """KG Recorder controller: device list, selection persist, stream attach.

    No recording session, no input inject, no CaptureGLImage signal wiring.
    Input signals stay on the view for later connection by the caller.
    """

    _sigDevicesChanged: SignalInstance = Signal()

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._deviceId: Optional[str] = None
        self._page: Any = None
        self._streamView: Any = None
        self._deviceCombo: Any = None
        self._deviceManager: Optional[deviceManager] = None
        self._streamSerial: Optional[str] = None
        self._deviceStream: Optional[LocalDeviceStream] = None
        self._comboWired: bool = False
        self._sigDevicesChanged.connect(self._refreshDeviceCombo)

    # -------------------------------------------------------------------------
    # MainWindow / Shell QSettings
    # -------------------------------------------------------------------------
    @property
    def settings(self) -> Optional[QSettings]:
        """Return the QSettings instance of the MainWindow or Shell."""
        if not hasattr(self, "_settings"):
            qsettings: QSettings = None
            node: Optional[QObject] = self.parent()
            while node is not None:
                settings = getattr(node, "settings", None)
                if isinstance(settings, QSettings):
                    qsettings = settings
                    break

                parentFn = getattr(node, "parent", None)
                node = parentFn() if callable(parentFn) else None

            self._settings = qsettings

        return self._settings
        

    def _loadPersistedDeviceId(self) -> Optional[str]:
        settings = self.settings
        if settings is None: return None

        try:
            raw = settings.value(C_SETTINGS_DEVICE_ID, "")
            cleaned = str(raw or "").strip()
            return cleaned or None
        
        except Exception as ex:
            warning(f"[KGRecorder] load persisted deviceId failed: {ex}")
            return None

    def _persistDeviceId(self, deviceId: Optional[str]) -> None:
        settings = self.settings
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

    # -------------------------------------------------------------------------
    # deviceManager
    # -------------------------------------------------------------------------
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

    # -------------------------------------------------------------------------
    # device combo
    # -------------------------------------------------------------------------
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

    # -------------------------------------------------------------------------
    # stream
    # -------------------------------------------------------------------------
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
                verbose(
                    f"[KGRecorder] stream attached serial={serial!r} via LocalDeviceStream"
                )
            except Exception as ex:
                error(f"[KGRecorder] ensureRunning failed serial={serial!r}", ex)
                error(f"[KGRecorder] traceback:\n{format_exc()}")

        createTask(_run)

    # -------------------------------------------------------------------------
    # public API
    # -------------------------------------------------------------------------
    @property
    def deviceId(self) -> Optional[str]:
        return self._deviceId

    def setDeviceId(self, deviceId: Optional[str]) -> None:
        cleaned = (deviceId or "").strip() or None
        if cleaned == self._deviceId:
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

    def bindPage(self, page: Any) -> None:
        self.unbindPage()
        self._page = page
        view = getattr(page, "_streamView", None)
        self._streamView = view
        self._deviceCombo = getattr(page, "_deviceCombo", None)
        if view is None:
            warning("[KGRecorder] bindPage: page has no _streamView")
            return
        verbose(f"[KGRecorder] bound to page streamView={type(view).__name__}")

        # No CaptureGLImage signal connections (option A).

        if not self._deviceId:
            self._deviceId = self._loadPersistedDeviceId()

        self._wireDeviceCombo()
        self._refreshDeviceCombo()
        if self._deviceId:
            self._attachStream(self._deviceId)

    def unbindPage(self) -> None:
        self._unwireDeviceCombo()
        self._detachStream()
        self._streamView = None
        self._deviceCombo = None
        self._page = None
