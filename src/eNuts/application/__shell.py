# ==================================================================================
from __future__ import annotations

# ==================================================================================
from PySide6.QtCore import QRect, QSettings, Qt

# ==================================================================================
from jAGQt.types.interface.window import iMainWindowBase

# ==================================================================================
from .__applicationInformation import ApplicationInformation
from .workspace import WorkSpace


# ==================================================================================
class Shell(ApplicationInformation):
    def _wInitializeUI(self: iMainWindowBase) -> None:
        verbose("[Shell] _wInitializeUI ENTER")
        try:
            central: WorkSpace = WorkSpace()
            verbose(f"[Shell] WorkSpace created objectName={central.objectName()!r}")
            self.setCentralWidget(central)
            verbose("[Shell] setCentralWidget done")

        except Exception as ex:
            error("[shell] initializeUI FAIL", ex)
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
