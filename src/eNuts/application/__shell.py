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
            print("[shell] intializeUI", flush=True)
            super()._wInitializeUI()

        except Exception as ex:
            error("[shell] intializeUI FAIL", ex)
    # ==================================================================================
    def _wInitializeSettings(self) -> None:
        company = self.company if hasattr(self, "company") else "jAGQt"
        appId: str = (
            self.applicationId if hasattr(self, "applicationId") else "modernWindow"
        )
        applicationId = self.applicationId or f"{appId}"
        self._qsettings = QSettings(company, applicationId)

    def _wRestoreWindowsState(self) -> None:
        print(self.applicationId)
        self.restoreWindowsState()

    def closeEvent(self, event) -> None:
        print(self.applicationId)
        self.saveWindowState()
        self._shutdownEvent.set()        
        super().closeEvent(event)