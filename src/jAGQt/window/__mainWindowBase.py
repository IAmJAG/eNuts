# ==================================================================================
# src/jAGQt/window/__mainWindowBase.py
# ==================================================================================
from __future__ import annotations

# ==================================================================================
from PySide6.QtCore import QRect, QSettings, Qt

# ==================================================================================
from jAGFx.workflow import workflow

# ==================================================================================
from .windowBase import WindowBase


# ==================================================================================
@workflow("InitializeUI", "InitializeSettings", "RestoreWindowsState")
class MainWindowBase(WindowBase):
    def __init__(self, name: str = None, *args, **kwargs) -> None:
        super().__init__(name, False, *args, **kwargs)

    def _wInitializeSettings(self) -> None:
        company = self.Company if hasattr(self, "Company") else "jAGQt"
        appId: str = self.ApplicationId if hasattr(self, "ApplicationId") else "ModernWindow"
        applicationId = f"{company}.{appId}"
        self._qsettings = QSettings(company, applicationId)

    def _wRestoreWindowsState(self) -> None:
        self.restoreWindowsState()

    def saveWindowState(self) -> None:
        self.Settings.setValue("geometry", self.geometry())
        self.Settings.setValue("windowState", int(self.windowState().value))

    def restoreWindowsState(self) -> None:
        if self.Settings.contains("geometry"):
            geo = self.Settings.value("geometry")
            if isinstance(geo, QRect) and geo.isValid():
                self.setGeometry(geo)

        if self.Settings.contains("windowState"):
            try:
                state = int(self.Settings.value("windowState"))
                self.setWindowState(Qt.WindowState(state))

            except (TypeError, ValueError):
                pass

    @property
    def Settings(self) -> QSettings:
        return self._qsettings

    @Settings.setter
    def Settings(self, value: QSettings) -> None:
        self._qsettings = value

    def closeEvent(self, event) -> None:
        self.saveWindowState()
        super().closeEvent(event)

    