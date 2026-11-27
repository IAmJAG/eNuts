# ==================================================================================
from __future__ import annotations

# ==================================================================================
from multiprocessing.synchronize import Event as syncEvent
from typing import Optional

# ==================================================================================
from PySide6.QtCore import QByteArray, QRect, QSettings, Qt
from PySide6.QtWidgets import QMainWindow

# ==================================================================================
from jAGFx.IPC import ProcessHost
from jAGFx.IPC.client import watcher
from jAGQt.types.interface.window import iMainWindowBase

# ==================================================================================
from ..services.clients.deviceManager import DeviceManager, messageHandler
from ..types.interface.application import iShell
from ..types.interface.services.device import iDeviceManager
from .__applicationInformation import ApplicationInformation
from .workspace import WorkSpace


# ==================================================================================
class Shell(iShell, ApplicationInformation):        
    def _wInitializeUI(self: iMainWindowBase | QMainWindow) -> None:
        verbose("ENTER")
        try:
            processHost: ProcessHost = ProcessHost(name="ProcessHost")
            self._deviceManager = processHost.start(
                worker=watcher, clientType=DeviceManager, 
                handler=messageHandler
            )

            central: WorkSpace = WorkSpace(title=self.title, parent=self)
            self.setCentralWidget(central)

            self._processHost: ProcessHost = processHost

        finally:
            verbose("EXIT")

    @property
    def host(self) -> ProcessHost:
        return self._processHost

    @property
    def deviceManager(self):
        return self._deviceManager

    def _wInitializeSettings(self) -> None:
        company = self.company or "jAGQt"
        appId = self.applicationId or "modernWindow"
        self._qsettings = QSettings(company, appId)

    def _wRestoreWindowsState(self) -> None:
        self.restoreWindowsState()

    def saveWindowState(self) -> None:
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
                self.setGeometry(geo)

        if self.settings.contains("windowState"):
            try:
                state = int(self.settings.value("windowState"))
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
    def deviceManager(self) -> iDeviceManager | None:
        return self._deviceManager

    def closeEvent(self, event) -> None:
        self.saveWindowState()
        self._shutdownEvent.set()
        super().closeEvent(event)
