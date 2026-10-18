# ==================================================================================
from __future__ import annotations

# ==================================================================================
from traceback import format_exc

# ==================================================================================
from PySide6.QtCore import QRect, QSettings, Qt

# ==================================================================================
from jAGQt.types.interface.window import iMainWindowBase

# ==================================================================================
from .__applicationInformation import ApplicationInformation
from .device import deviceManager
from .workspace import WorkSpace


# ==================================================================================
class Shell(ApplicationInformation):
    def _wInitializeUI(self: iMainWindowBase) -> None:
        verbose("[Shell] _wInitializeUI ENTER")
        try:
            mgr = deviceManager(self._shutdownEvent)
            self._deviceManager = mgr

            central: WorkSpace = WorkSpace(deviceMgr=mgr)
            verbose(
                f"[Shell] WorkSpace created objectName={central.objectName()!r}"
            )
            self.setCentralWidget(central)
            self._workSpace = central
            verbose("[Shell] setCentralWidget done")

            mgr.runDiscovery()
            verbose("[Shell] deviceManager.runDiscovery started")

        except Exception as ex:
            error("[Shell] _wInitializeUI FAIL", ex)
            error(f"[Shell] _wInitializeUI traceback:\n{format_exc()}")
            raise
        finally:
            verbose("[Shell] _wInitializeUI EXIT")

    # ==================================================================================
    def _wInitializeSettings(self) -> None:
        company = self.company or "jAGQt"
        appId = self.applicationId or "modernWindow"
        self._qsettings = QSettings(company, appId)

    def _wRestoreWindowsState(self) -> None:
        self.restoreWindowsState()

    def saveWindowState(self) -> None:
        self.settings.setValue("geometry", self.geometry())
        self.settings.setValue("windowState", int(self.windowState().value))

    def restoreWindowsState(self) -> None:
        if self.settings.contains("geometry"):
            geo = self.settings.value("geometry")
            if isinstance(geo, QRect) and geo.isValid():
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
    def DeviceManager(self) -> deviceManager | None:
        return getattr(self, "_deviceManager", None)

    def closeEvent(self, event) -> None:
        self.saveWindowState()
        self._shutdownEvent.set()
        super().closeEvent(event)
