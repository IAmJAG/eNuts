# ==================================================================================
from __future__ import annotations

# ==================================================================================
from PySide6.QtCore import QRect, QSettings, Qt

# ==================================================================================
from jAGQt.types.interface.window import iMainWindowBase

# ==================================================================================
from .__applicationInformation import ApplicationInformation


# ==================================================================================
class Shell(ApplicationInformation):
    def _wInitializeUI(self: iMainWindowBase) -> None:
        try:
            super()._wInitializeUI()
            self.Title = self.title

        except Exception as ex:
            error("[shell] initializeUI FAIL", ex)

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
            except (TypeError, ValueError):
                pass

    @property
    def settings(self) -> QSettings:
        return self._qsettings

    @settings.setter
    def settings(self, value: QSettings) -> None:
        self._qsettings = value

    def closeEvent(self, event) -> None:
        self.saveWindowState()
        self._shutdownEvent.set()
        super().closeEvent(event)
