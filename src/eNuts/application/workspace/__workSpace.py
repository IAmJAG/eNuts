# ==================================================================================
from __future__ import annotations

# ==================================================================================
from traceback import format_exc
from typing import Dict, List, Optional, Set

# ==================================================================================
from PySide6.QtCore import Qt, Signal, SignalInstance
from PySide6.QtWidgets import QBoxLayout, QSizePolicy, QStackedWidget, QWidget

# ==================================================================================
from fluxCore.types.interface.device import iDevice
from jAGFx.workflow import workflow
from jAGQt.options import AnimationOptions, SideBarOptions
from jAGQt.widgets.components import ComponentBase, ObjectName
from jAGQt.widgets.page import Page
from jAGQt.widgets.sideBar import SideBar, SideBarMenuItem, eSideBarState
from utilities.io import getICONPath

# ==================================================================================
from ...UI.navigation import buildSmokeTestSideBarMenu, pageKeyOf, setPageKey
from ...UI.pages import (
    C_DEVICE_NONE,
    PAGE_DASHBOARD,
    PAGE_DEVICES,
    buildBlankPage,
    buildNavigationPages,
    devicePageKeyFromId,
)
from ..device import (
    DEVICE_ADDED_EVENT,
    DEVICE_INITIALIZED_EVENT,
    DEVICE_REMOVED_EVENT,
    deviceManager,
)

# ==================================================================================
QSPolicy = QSizePolicy.Policy
StyleBackground = Qt.WidgetAttribute.WA_StyledBackground
C_SIDEBAR_ANIMATION_TYPE: str = "jAGQt.animations.RubberBand"
C_SIDEBAR_ANIMATION_MS: int = 280
# ==================================================================================


# ==================================================================================
@workflow
class WorkSpace(ComponentBase, ObjectName, QWidget):
    OBJECT_NAME = "W_WORKSPACE"

    # Cross-thread safe bridge from deviceManager -> Qt main thread.
    _sigDevicesReady: SignalInstance = Signal(object)
    _sigDeviceAdded: SignalInstance = Signal(object)
    _sigDeviceRemoved: SignalInstance = Signal(object)

    def __init__(
        self, deviceMgr: Optional[deviceManager] = None,
        *args, **kwargs,
    ) -> None:
        verbose("[WorkSpace] __init__ ENTER")
        try:
            super().__init__(*args, **kwargs)
            self._sideBar: Optional[SideBar] = None
            self._stack: Optional[QStackedWidget] = None
            self._pages: Dict[str, Page] = {}
            self._pageIndex: Dict[str, int] = {}
            self._devicesHeader: Optional[SideBarMenuItem] = None
            self._deviceManager: Optional[deviceManager] = deviceMgr
            self._devicePageKeys: Set[str] = set()

        except Exception as ex:
            error("[WorkSpace] __init__ FAIL", ex)
            error(f"[WorkSpace] __init__ traceback:\n{format_exc()}")
            raise

        verbose(f"[WorkSpace] __init__ EXIT objectName={self.objectName()!r}")

    def _wInitializeUI(self) -> None:
        verbose("[WorkSpace] _wInitializeUI ENTER")
        try:
            self.setAttribute(StyleBackground, True)
            self.setStyleSheet("background-color: #1e1e1e;")

            expandPath: str = getICONPath("expand.png")
            collapsePath: str = getICONPath("collapse.png")

            sideBarOptions = SideBarOptions(
                animation=C_SIDEBAR_ANIMATION_TYPE,
            )
            animationOptions = AnimationOptions(
                name="RubberBand",
                durationMs=C_SIDEBAR_ANIMATION_MS,
            )

            sideBar: SideBar = SideBar(
                icons={
                    eSideBarState.Expanded: collapsePath,
                    eSideBarState.Collapsed: expandPath,
                },
                title="eNuts",
                initialState=eSideBarState.Expanded,
                options=sideBarOptions,
                animationOptions=animationOptions,
            )

            menu, settings, devicesHeader = buildSmokeTestSideBarMenu()
            sideBar.Content = menu
            sideBar.Footer = settings
            self._devicesHeader = devicesHeader

            stack: QStackedWidget = QStackedWidget()
            stack.setObjectName("W_WORKSPACE_STACK")
            stack.setSizePolicy(QSPolicy.Expanding, QSPolicy.Expanding)

            pages = buildNavigationPages()
            pageIndex: Dict[str, int] = {}
            for key, page in pages.items():
                idx = stack.addWidget(page)
                pageIndex[key] = idx

            if PAGE_DASHBOARD in pageIndex:
                stack.setCurrentIndex(pageIndex[PAGE_DASHBOARD])

            menu.itemClicked.connect(self._onNavItemClicked)
            settings.clicked.connect(self._onNavItemClicked)

            layout: QBoxLayout = QBoxLayout(QBoxLayout.Direction.LeftToRight)
            layout.setSpacing(0)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(sideBar)
            layout.addWidget(stack, 1)

            if hasattr(self, "_layout"):
                self._layout = layout
                del self._layout

            self.setLayout(layout)
            self._sideBar = sideBar
            self._stack = stack
            self._pages = pages
            self._pageIndex = pageIndex

            self._sigDevicesReady.connect(self._onDevicesReadyUi)
            self._sigDeviceAdded.connect(self._onDeviceAddedUi)
            self._sigDeviceRemoved.connect(self._onDeviceRemovedUi)
            self._bindDeviceManager(self._deviceManager)

            verbose(
                f"[WorkSpace] _wInitializeUI EXIT "
                f"deviceMgr={'yes' if self._deviceManager else 'no'}"
            )
        except Exception as ex:
            error("[WorkSpace] _wInitializeUI FAIL", ex)
            error(f"[WorkSpace] _wInitializeUI traceback:\n{format_exc()}")
            raise

    def _onNavItemClicked(self, item: object) -> None:
        key = pageKeyOf(item)
        if key is None:
            if isinstance(item, SideBarMenuItem):
                verbose(
                    f"[WorkSpace] nav skip caption={item.Caption!r} (no pageKey)"
                )
            return
        self.showPage(key)

    def showPage(self, key: str) -> bool:
        stack = self._stack
        index = self._pageIndex.get(key)
        if stack is None or index is None:
            warning(f"[WorkSpace] unknown page key={key!r}")
            return False
        stack.setCurrentIndex(index)
        page = self._pages.get(key)
        title = page.Title if page is not None else key
        verbose(f"[WorkSpace] showPage key={key!r} title={title!r} index={index}")
        return True

    def _bindDeviceManager(self, mgr: Optional[deviceManager]) -> None:
        self._deviceManager = mgr
        if mgr is None:
            return
        mgr.subscribe(DEVICE_INITIALIZED_EVENT, self._onDevicesReadyEvent)
        mgr.subscribe(DEVICE_ADDED_EVENT, self._onDeviceAddedEvent)
        mgr.subscribe(DEVICE_REMOVED_EVENT, self._onDeviceRemovedEvent)
        verbose("[WorkSpace] subscribed to deviceManager events")

    def _onDevicesReadyEvent(self, mgr: object) -> None:
        self._sigDevicesReady.emit(mgr)

    def _onDeviceAddedEvent(self, device: object) -> None:
        self._sigDeviceAdded.emit(device)

    def _onDeviceRemovedEvent(self, device: object) -> None:
        self._sigDeviceRemoved.emit(device)

    def _onDevicesReadyUi(self, mgr: object) -> None:
        try:
            devices = self._listDevices(mgr)
            verbose(f"[WorkSpace] devices ready count={len(devices)}")
            self._syncDevicesList(devices)
        except Exception as ex:
            error("[WorkSpace] _onDevicesReadyUi FAIL", ex)
            error(f"[WorkSpace] traceback:\n{format_exc()}")

    def _onDeviceAddedUi(self, device: object) -> None:
        try:
            if not self._isDevice(device):
                return
            verbose(f"[WorkSpace] device added id={device.id!r} name={device.name!r}")
            self._registerDevice(device)
            self._rebuildDevicesMenuLeaves()
        except Exception as ex:
            error("[WorkSpace] _onDeviceAddedUi FAIL", ex)
            error(f"[WorkSpace] traceback:\n{format_exc()}")

    def _onDeviceRemovedUi(self, device: object) -> None:
        try:
            if not self._isDevice(device):
                return
            key = devicePageKeyFromId(str(device.id))
            verbose(f"[WorkSpace] device removed id={device.id!r} key={key!r}")
            self._unregisterDevicePage(key)
            self._rebuildDevicesMenuLeaves()
        except Exception as ex:
            error("[WorkSpace] _onDeviceRemovedUi FAIL", ex)
            error(f"[WorkSpace] traceback:\n{format_exc()}")

    @staticmethod
    def _isDevice(obj: object) -> bool:
        return hasattr(obj, "id") and hasattr(obj, "name")

    @staticmethod
    def _listDevices(mgr: object) -> List[iDevice]:
        if mgr is None:
            return []
        if hasattr(mgr, "values"):
            return [d for d in list(mgr.values()) if hasattr(d, "id")]
        return []

    def _syncDevicesList(self, devices: List[iDevice]) -> None:
        liveKeys: Set[str] = set()
        for device in devices:
            if not self._isDevice(device):
                continue
            key = self._registerDevice(device)
            liveKeys.add(key)

        for key in list(self._devicePageKeys - liveKeys):
            self._unregisterDevicePage(key)

        self._rebuildDevicesMenuLeaves()

    def _registerDevice(self, device: iDevice) -> str:
        key = devicePageKeyFromId(str(device.id))
        title = (device.name or "").strip() or str(device.id)
        self._ensureDevicePage(key, title)
        self._devicePageKeys.add(key)
        return key

    def _ensureDevicePage(self, key: str, title: str) -> None:
        stack = self._stack
        if stack is None:
            return
        if key in self._pages:
            page = self._pages[key]
            try:
                page.Title = title

            except Exception:
                pass
            return

        page = buildBlankPage(key, title, "Device")
        idx = stack.addWidget(page)
        self._pages[key] = page
        self._pageIndex[key] = idx
        verbose(f"[WorkSpace] registered device page key={key!r} index={idx}")

    def _unregisterDevicePage(self, key: str) -> None:
        if key == C_DEVICE_NONE or key not in self._pages:
            self._devicePageKeys.discard(key)
            return
        stack = self._stack
        if stack is None:
            return

        currentKey = None
        cur = stack.currentIndex()
        for k, i in self._pageIndex.items():
            if i == cur:
                currentKey = k
                break
        if currentKey == key:
            self.showPage(PAGE_DEVICES)

        page = self._pages.pop(key, None)
        self._pageIndex.pop(key, None)
        self._devicePageKeys.discard(key)
        if page is not None:
            stack.removeWidget(page)
            page.deleteLater()
        self._rebuildPageIndex()
        verbose(f"[WorkSpace] unregistered device page key={key!r}")

    def _rebuildPageIndex(self) -> None:
        stack = self._stack
        if stack is None:
            return
        self._pageIndex.clear()
        for i in range(stack.count()):
            w = stack.widget(i)
            if isinstance(w, Page):
                self._pageIndex[str(w.Id)] = i

    def _rebuildDevicesMenuLeaves(self) -> None:
        header = self._devicesHeader
        if header is None:
            return

        devices = self._listDevices(self._deviceManager)
        verbose(
            f"[WorkSpace] rebuild devices menu "
            f"mgr_count={len(devices)} prior_children={len(header.Children)}"
        )

        # Drop every leaf (including "(no devices)") then rebuild from mgr.
        header.clearChildren()

        if not devices:
            leaf = header.addChild("(no devices)")
            setPageKey(leaf, C_DEVICE_NONE)
            self._ensureDevicePage(C_DEVICE_NONE, "(no devices)")
            header.Expanded = True
            verbose("[WorkSpace] devices menu -> (no devices)")
            return

        for device in devices:
            if not self._isDevice(device):
                continue
            key = devicePageKeyFromId(str(device.id))
            caption = (device.name or "").strip() or str(device.id)
            leaf = header.addChild(caption)
            setPageKey(leaf, key)
            self._ensureDevicePage(key, caption)

        header.Expanded = True
        captions = [c.Caption for c in header.Children]
        verbose(
            f"[WorkSpace] devices menu -> {len(header.Children)} leaf(s) "
            f"captions={captions!r}"
        )

    @property
    def SideBar(self) -> Optional[SideBar]:
        return self._sideBar

    @property
    def Stack(self) -> Optional[QStackedWidget]:
        return self._stack

    @property
    def Pages(self) -> Dict[str, Page]:
        return dict(self._pages)

    @property
    def DeviceManager(self) -> Optional[deviceManager]:
        return self._deviceManager
