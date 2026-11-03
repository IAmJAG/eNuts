# ==================================================================================
from __future__ import annotations

# ==================================================================================
from traceback import format_exc
from typing import Optional

# ==================================================================================
from PySide6.QtCore import QByteArray, QRect, QSettings, Qt
from PySide6.QtWidgets import QMainWindow

# ==================================================================================
from jAGQt.types.interface.window import iMainWindowBase

# ==================================================================================
from ..types.interface.application import iShell
from ..types.interface.application.device import iDeviceManager
from ..UI.navigation.__pageKeys import PAGE_KG_RECORDER
from .__applicationInformation import ApplicationInformation
from .device import DeviceManager
from .workspace import WorkSpace


# ==================================================================================
class Shell(iShell, ApplicationInformation):
    def _wInitializeUI(self: iMainWindowBase | QMainWindow) -> None:
        verbose("ENTER")
        try:        
            mgr: iDeviceManager = DeviceManager(self._shutdownEvent)
            self._deviceManager = mgr
            
            central: WorkSpace = WorkSpace(title=self.title, parent=self)
            self.setCentralWidget(central)

            mgr.runDiscovery()           

        except Exception as ex:
            error("FAIL", ex)

        finally:
            verbose("EXIT")

    def _wInitializeSettings(self) -> None:
        company = self.company or "jAGQt"
        appId = self.applicationId or "modernWindow"
        self._qsettings = QSettings(company, appId)

    def _wRestoreWindowsState(self) -> None:
        self.restoreWindowsState()

    def saveWindowState(self) -> None:
        # saveGeometry encodes normal size/pos + maximized/fullscreen.
        # geometry() alone is the *current* frame (maximized rect) and loses normal size.
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", int(self.windowState().value))

    def restoreWindowsState(self) -> None:
        if self.settings.contains("geometry"):
            geo = self.settings.value("geometry")
            if isinstance(geo, QByteArray) and not geo.isEmpty():
                self.restoreGeometry(geo)
            elif isinstance(geo, (bytes, bytearray)) and len(geo) > 0:
                self.restoreGeometry(QByteArray(geo))
            elif isinstance(geo, QRect) and geo.isValid():
                # Legacy: plain QRect from older builds (no normal-size memory).
                self.setGeometry(geo)

        if self.settings.contains("windowState"):
            try:
                state = int(self.settings.value("windowState"))
                # Re-apply after geometry so maximized/minimized matches last close.
                self.setWindowState(Qt.WindowState(state))
            except (TypeError, ValueError) as ex:
                warning(
                    f"[Shell] restoreWindowsState invalid windowState={self.settings.value('windowState')!r}: {ex}"
                )

    @property
    def settings(self) -> QSettings:
        return self._qsettings

    @settings.setter
    def settings(self, value: QSettings) -> None:
        self._qsettings = value

    @property
    def deviceManager(self) -> Optional[iDeviceManager]:
        return self._deviceManager

    @property
    def KGRecorder(self) -> Optional[KGRecorder]:
        return getattr(self, "_kgRecorder", None)

    def closeEvent(self, event) -> None:
        self.saveWindowState()

        mgr = self.deviceManager

        if mgr is not None:
            try: mgr.stopAll()
            except Exception as ex:
                warning(f"[Shell] deviceManager.stopAll failed: {ex}")

        self._shutdownEvent.set()
        super().closeEvent(event)
