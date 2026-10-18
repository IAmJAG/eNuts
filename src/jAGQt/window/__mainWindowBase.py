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
    OBJECT_NAME = "W_MAIN_WINDOW_BASE"
    def __init__(
        self, company: str = None, applicationId: str = None, *args, **kwargs,
    ) -> None:
        super().__init__(False, *args, **kwargs)
        self._applicationId = applicationId
        self._company = company

    @property
    def company(self) -> str:
        return self._company

    @company.setter
    def company(self, value: str):
        self._company = value

    @property
    def applicationId(self) -> str:
        return self._applicationId

    @applicationId.setter
    def applicationId(self, value: str):
        self._applicationId = value        

    def _wInitializeSettings(self) -> None:        
        self._qsettings = QSettings(self.Company, self.ApplicationId)

    def _wRestoreWindowsState(self) -> None:
        self.restoreWindowsState()

    def saveWindowState(self) -> None:
        self.Settings.setValue("geometry", self.geometry())
        self.Settings.setValue("windowState", int(self.windowState().value))

    def restoreWindowsState(self) -> None:
        if self.Settings.contains("geometry"):
            lGeo = self.Settings.value("geometry")
            if isinstance(lGeo, QRect) and lGeo.isValid():
                self.setGeometry(lGeo)

        if self.Settings.contains("windowState"):
            try:
                lState = int(self.Settings.value("windowState"))
                self.setWindowState(Qt.WindowState(lState))
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
        super().closeEvent(event)

    