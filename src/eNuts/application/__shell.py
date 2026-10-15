# ==================================================================================
from __future__ import annotations

# ==================================================================================
from PySide6.QtCore import QSettings

# ==================================================================================
from jAGQt.types.interface.window import iMainWindowBase

# ==================================================================================
from ..types.interface.application import iShell
from .__applicationInformation import ApplicationInformation
from .workspace import WorkSpace


# ==================================================================================
class Shell(ApplicationInformation):
    def _wInitializeUI(self: iMainWindowBase) -> None:
        try:
            super()._wInitializeUI()

        except Exception as ex:
            error("[shell] initializeUI FAIL", ex)
    # ==================================================================================
    def _wInitializeSettings(self) -> None:
        company = self.Company if hasattr(self, "Company") else "jAGQt"
        appId: str = (
            self.ApplicationId if hasattr(self, "ApplicationId") else "ModernWindow"
        )
        applicationId = f"{company}.{appId}"
        self._qsettings = QSettings(company, applicationId)

    def _wRestoreWindowsState(self) -> None:
        self.restoreWindowsState()

    def closeEvent(self, event) -> None:
        self.saveWindowState()
        self._shutdownEvent.set()
        super().closeEvent(event)
