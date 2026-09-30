# ==================================================================================
# src/jAGQt/window/__mainWindowBase.py
# ==================================================================================
from PySide6.QtCore import QSettings

# ==================================================================================
from jAGFx.workflow import workflow

# ==================================================================================
from .windowBase import WindowBase


# ==================================================================================
@workflow("InitializeUI", "InitializeSettings", "RestoreWindowsState")
class MainWindowBase(WindowBase):
    """Richer foundation for application main-window and dashboard classes."""

    def __init__(self, name: str = None, frameless: bool = False, *args, **kwargs) -> None:
        super().__init__(name, frameless, *args, **kwargs)

    def _wInitializeSettings(self) -> None:
        company = self.Company if hasattr(self, "Company") else "jAGQt"
        applicationId = self.ApplicationId if hasattr(self, "ApplicationId") else "jAGQt::ModernWindow"
        self._qsettings = QSettings(company, applicationId)

    def _wRestoreWindowsState(self) -> None:
        self.restoreWindowsState()

    def saveWindowState(self) -> None:
        self.Settings.setValue("geometry", self.geometry())
        self.Settings.setValue("windowState", self.windowState())

    def restoreWindowsState(self) -> None:
        if self.Settings.contains("geometry"):
            self.setGeometry(self.Settings.value("geometry"))

        if self.Settings.contains("windowState"):
            self.setWindowState(self.Settings.value("windowState"))

    def closeEvent(self, event) -> None:
        self.saveWindowState()
        super().closeEvent(event)

    @property
    def Settings(self) -> QSettings:
        return self._qsettings

    @Settings.setter
    def Settings(self, value: QSettings):
        self._qsettings = value
