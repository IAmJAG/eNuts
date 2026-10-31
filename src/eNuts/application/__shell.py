# ==================================================================================
from __future__ import annotations

# ==================================================================================
from traceback import format_exc

# ==================================================================================
from PySide6.QtCore import QRect, QSettings, Qt
from PySide6.QtWidgets import QMainWindow

# ==================================================================================
from jAGQt.types.interface.window import iMainWindowBase

from ..UI.navigation.__pageKeys import PAGE_KG_RECORDER

# ==================================================================================
from .__applicationInformation import ApplicationInformation
from .device import deviceManager
from .recorder import KGRecorder
from .workspace import WorkSpace


# ==================================================================================
class Shell(ApplicationInformation):
    def _wInitializeUI(self: iMainWindowBase | QMainWindow) -> None:
        verbose("ENTER")
        try:
            # IMPORTANT: parent NEED to be preset before setting the central widget
            central: WorkSpace = WorkSpace(title=self.title, parent=self)
            self.setCentralWidget(central)
            
        except Exception as ex:
            error("FAIL", ex)

        finally:
            verbose("EXIT")

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
    def KGRecorder(self) -> KGRecorder | None:
        return getattr(self, "_kgRecorder", None)

    def closeEvent(self, event) -> None:
        self.saveWindowState()
        self._shutdownEvent.set()
        super().closeEvent(event)
