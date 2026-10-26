# ==================================================================================
from __future__ import annotations

# ==================================================================================
from traceback import format_exc

# ==================================================================================
from PySide6.QtCore import QRect, QSettings, Qt

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
    def _wInitializeUI(self: iMainWindowBase) -> None:
        verbose(f"[{self.__class__.__name__}] _wInitializeUI ENTER")
        try:
            mgr = deviceManager(self._shutdownEvent)

            central: WorkSpace = WorkSpace(deviceMgr=mgr, title=self.title)
            self.setCentralWidget(central)
            self._workSpace = central
            self._deviceManager = mgr

            # Controller persists across page strip — bind still runs so
            # bindPage/command wiring can be inspected against a basic Page.
            recorder = KGRecorder(self)
            recorder.setDeviceManager(mgr)
            self._kgRecorder = recorder
            self._bindKGRecorder(central, recorder)

            mgr.runDiscovery()
            verbose("[Shell] deviceManager.runDiscovery started")

        except Exception as ex:
            error(f"[{self.__class__.__name__}] _wInitializeUI FAIL", ex)
            error(f"[{self.__class__.__name__}] traceback:\n{format_exc()}")

        finally:
            verbose(f"[{self.__class__.__name__}] _wInitializeUI EXIT")

    def _bindKGRecorder(self, workSpace: WorkSpace, recorder: KGRecorder) -> None:
        """Attach KGRecorder to the kg-recorder page view (minimal Shell logic)."""
        try:
            pages = getattr(workSpace, "Pages", None) or {}
            if not pages:
                pages = getattr(workSpace, "_pages", None) or {}
            page = pages.get(PAGE_KG_RECORDER)
            if page is None:
                warning("[Shell] kg-recorder page not found; recorder unbound")
                return

            recorder.bindPage(page)
            self._wireKGRecorderCommands(page, recorder)
            self._wireKGRecorderViews(page, recorder)
            verbose("[Shell] KGRecorder bound to page")

        except Exception as ex:
            error("[Shell] _bindKGRecorder FAIL", ex)
            error(f"[Shell] traceback:\n{format_exc()}")

    def _wireKGRecorderCommands(self, page: object, recorder: KGRecorder) -> None:
        commandBar = getattr(page, "_commandBar", None)
        if commandBar is None:
            warning("[Shell] kg-recorder page has no CommandBar")
            return

        def _findButtons() -> dict[str, object]:
            found: dict[str, object] = {}
            try:
                buttons = getattr(commandBar, "_buttons", None) or []
                for btn in buttons:
                    text = btn.text() if hasattr(btn, "text") else ""
                    if text:
                        found[text] = btn
                groups = getattr(commandBar, "_groups", None) or {}
                for group in groups.values():
                    gButtons = getattr(group, "_buttons", None) or []
                    for btn in gButtons:
                        text = btn.text() if hasattr(btn, "text") else ""
                        if text:
                            found[text] = btn
            except Exception:
                pass
            return found

        byCaption = _findButtons()
        mapping = {
            "Start": recorder.start,
            "Stop": recorder.stop,
            "Clear": recorder.clear,
            "Save": lambda: recorder.save(),
            "Open": lambda: recorder.open(""),
        }
        for caption, slot in mapping.items():
            btn = byCaption.get(caption)
            if btn is None:
                warning(f"[Shell] kg-recorder command missing: {caption!r}")
                continue
            try:
                btn.clicked.connect(slot)
            except Exception as ex:
                warning(f"[Shell] connect {caption!r} failed: {ex}")

        deviceCombo = getattr(page, "_deviceCombo", None)
        if deviceCombo is not None:

            def _onDeviceChanged(index: int) -> None:
                data = deviceCombo.itemData(index)
                serial = str(data) if data is not None else None
                recorder.setDeviceId(serial)

            try:
                deviceCombo.currentIndexChanged.connect(_onDeviceChanged)
            except Exception as ex:
                warning(f"[Shell] device combo connect failed: {ex}")

    def _wireKGRecorderViews(self, page: object, recorder: KGRecorder) -> None:
        statusLabel = getattr(page, "_statusLabel", None)
        eventList = getattr(page, "_eventList", None)

        if statusLabel is not None:

            def _onStatus(text: str) -> None:
                try:
                    statusLabel.setText(text)
                except Exception:
                    pass

            recorder.statusTextChanged.connect(_onStatus)

        if eventList is not None:

            def _onEvents(events: object) -> None:
                try:
                    eventList.clear()
                    if not isinstance(events, list):
                        return
                    for entry in events:
                        if not isinstance(entry, dict):
                            continue
                        t = entry.get("t", 0)
                        kind = entry.get("type", "?")
                        action = entry.get("action", "")
                        if kind == "key":
                            detail = entry.get("text") or entry.get("key")
                        else:
                            detail = f"{entry.get('x', 0):.0f},{entry.get('y', 0):.0f}"
                        eventList.addItem(f"{t:8.1f}  {kind}/{action}  {detail}")
                except Exception:
                    pass

            recorder.eventsChanged.connect(_onEvents)

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
    def DeviceManager(self) -> deviceManager | None:
        return getattr(self, "_deviceManager", None)

    @property
    def KGRecorder(self) -> KGRecorder | None:
        return getattr(self, "_kgRecorder", None)

    def closeEvent(self, event) -> None:
        self.saveWindowState()
        self._shutdownEvent.set()
        recorder = getattr(self, "_kgRecorder", None)
        if recorder is not None:
            try:
                recorder.unbindPage()
            except Exception as ex:
                warning(f"[Shell] KGRecorder.unbindPage failed: {ex}")
        ws = getattr(self, "_workSpace", None)
        if ws is not None and hasattr(ws, "detachAllStreams"):
            try:
                ws.detachAllStreams()
            except Exception as ex:
                warning(f"[Shell] detachAllStreams failed: {ex}")
        mgr = getattr(self, "_deviceManager", None)
        if mgr is not None:
            try:
                mgr.stopAll()
            except Exception as ex:
                warning(f"[Shell] stopAll failed: {ex}")
        super().closeEvent(event)
