# ==================================================================================
from __future__ import annotations

# ==================================================================================
from PySide6.QtCore import QSettings

# ==================================================================================
from jAGQt.types.interface.window import iMainWindowBase

# ==================================================================================
from .__applicationInformation import ApplicationInformation


# ==================================================================================
class Shell(ApplicationInformation):
    def _wInitializeUI(self: iMainWindowBase) -> None:
        try:
            super()._wInitializeUI()

        except Exception as ex:
            error("[shell] initializeUI FAIL", ex)
    # ==================================================================================
    def _wInitializeSettings(self) -> None:
        company = self.company if hasattr(self, "company") else "jAGQt"
        appId: str = (
            self.applicationId if hasattr(self, "applicationId") else "modernWindow"
        )
        applicationId = self.applicationId or f"{appId}"
        self._qsettings = QSettings(company, applicationId)

    def _wRestoreWindowsState(self) -> None:
        self.restoreWindowsState()

    def closeEvent(self, event) -> None:
        self.saveWindowState()
        self._shutdownEvent.set()
        super().closeEvent(event)
