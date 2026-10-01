# ==================================================================================
# src/jAGQt/window/__mainWindowBase.py
# ==================================================================================
from __future__ import annotations

from enum import Enum
from typing import Optional

# ==================================================================================
from PySide6.QtCore import QRect, QSettings, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QWidget

# ==================================================================================
from jAGFx.workflow import workflow

# ==================================================================================
from ..types import ShowAnimation
from .windowBase import WindowBase


# ==================================================================================
@workflow("InitializeUI", "InitializeSettings", "RestoreWindowsState")
class MainWindowBase(WindowBase):
    """Richer foundation for application main-window and dashboard classes."""

    def __init__(
        self, name: str = None,
        showAnimation: ShowAnimation | str = ShowAnimation.Popup,
        showAnimationDurationMs: int = 280, *args, **kwargs,
    ) -> None:
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
    def Settings(self) -> QSettings:
        return self._qsettings

    @Settings.setter
    def Settings(self, value: QSettings) -> None:
        self._qsettings = value

    def closeEvent(self, event) -> None:
        self.saveWindowState()
        super().closeEvent(event)

    