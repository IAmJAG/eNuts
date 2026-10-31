# ==================================================================================
from __future__ import annotations

# ==================================================================================
from traceback import format_exc
from typing import Optional

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
    def _ensureManagers(self) -> None:
        """Create deviceManager + KGRecorder once and wire them."""
        if getattr(self, "_deviceManager", None) is None:
            mgr = deviceManager(self._shutdownEvent)
            self._deviceManager = mgr
            mgr.runDiscovery()
            verbose("[Shell] deviceManager created; discovery scheduled")

        if getattr(self, "_kgRecorder", None) is None:
            recorder = KGRecorder(parent=self)
            self._kgRecorder = recorder
            recorder.setDeviceManager(self._deviceManager)
            verbose("[Shell] KGRecorder created and wired to deviceManager")

    def _bindKgRecorderPage(self, workspace: WorkSpace) -> None:
        recorder = self.KGRecorder
        if recorder is None:
            return
        pages = getattr(workspace, "Pages", None) or {}
        page = pages.get(PAGE_KG_RECORDER)
        if page is None:
            warning("[Shell] KG recorder page not found; bind skipped")
            return
        try:
            recorder.bindPage(page)
            verbose("[Shell] KGRecorder bound to page")
        except Exception as ex:
            error("[Shell] KGRecorder.bindPage failed", ex)

    def _wInitializeUI(self: iMainWindowBase | QMainWindow) -> None:
        verbose("ENTER")
        try:
            self._ensureManagers()

            # IMPORTANT: parent NEED to be preset before setting the central widget
            central: WorkSpace = WorkSpace(title=self.title, parent=self)
            self.setCentralWidget(central)

            self._bindKgRecorderPage(central)

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
    def deviceManager(self) -> Optional[deviceManager]:
        return getattr(self, "_deviceManager", None)

    @property
    def KGRecorder(self) -> Optional[KGRecorder]:
        return getattr(self, "_kgRecorder", None)

    def closeEvent(self, event) -> None:
        self.saveWindowState()
        mgr = self.deviceManager
        if mgr is not None:
            try:
                mgr.stopAll()
            except Exception as ex:
                warning(f"[Shell] deviceManager.stopAll failed: {ex}")
        self._shutdownEvent.set()
        super().closeEvent(event)
