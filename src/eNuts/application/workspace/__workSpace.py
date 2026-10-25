# ==================================================================================
from __future__ import annotations

# ==================================================================================
from traceback import format_exc
from typing import Callable, Dict, List, Optional, Set

# ==================================================================================
from PySide6.QtCore import Qt, Signal, SignalInstance
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QBoxLayout, QSizePolicy, QStackedWidget, QWidget

# ==================================================================================
from fluxCore.emitters.scrcpy import SCRCPYEmitter
from fluxCore.types.interface.device import iDevice
from jAGFx.workflow import workflow
from jAGQt.options import AnimationOptions, SideBarOptions
from jAGQt.widgets.components import ComponentBase, ObjectName
from jAGQt.widgets.page import Page
from jAGQt.widgets.sideBar import SideBar, SideBarMenuItem, eSideBarState
from utilities.io import getICONPath

# ==================================================================================
from ...UI.navigation import buildSideBarMenu, pageKeyOf, setPageKey
from ...UI.pages import (
    G_DEVICE_KEY_PREFIX,
    G_DEVICE_NONE,
    PAGE_DASHBOARD,
    PAGE_DEVICES,
    buildDevicePage,
    buildNavigationPages,
    devicePageKeyFromId,
)
from ...UI.pages.__devicePage import DeviceFrameBridge
from ...UI.pages.__pageKeys import serialFromPageKey
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
C_ON_FRAME = "ON_FRAME"
# ==================================================================================


# ==================================================================================
@workflow("InitializeUI", "BuildMenu")
class WorkSpace(ComponentBase, ObjectName, QWidget):
    OBJECT_NAME = "W_WORKSPACE"

    _sigDevicesReady: SignalInstance = Signal(object)
    _sigDeviceAdded: SignalInstance = Signal(object)
    _sigDeviceRemoved: SignalInstance = Signal(object)

    def __init__(
        self, deviceMgr: Optional[deviceManager] = None, 
        title: str = "eNuts",
        *args, **kwargs
    ) -> None:
        debug(f"[{self.__class__.__name__}] __init__ ENTER")
        try:
            super().__init__(*args, **kwargs)
            self._sideBar: Optional[SideBar] = None
            self._stack: Optional[QStackedWidget] = None
            self._pages: Dict[str, Page] = {}
            self._pageIndex: Dict[str, int] = {}
            self._title: str = title

            self._devicesHeader: Optional[SideBarMenuItem] = None
            self._deviceManager: Optional[deviceManager] = deviceMgr
            self._devicePageKeys: Set[str] = set()
            self._activeStreamSerial: Optional[str] = None
            self._frameHandlerBySerial: Dict[str, Callable] = {}
            # Long-lived bridges (survive page teardown order issues).
            self._bridges: Dict[str, DeviceFrameBridge] = {}

        except Exception as ex:
            error(f"[{self.__class__.__name__}] __init__ FAIL", ex)

        finally:
            objName: str = f"{self.objectName()!r}"
            debug(f"[{self.__class__.__name__}] __init__ EXIT objectName={objName}")

    def _buildSideBar(self) -> None:
        # SideBar
        expandPath: str = getICONPath("expand.png")
        collapsePath: str = getICONPath("collapse.png")

        sideBarOptions = SideBarOptions(animation=C_SIDEBAR_ANIMATION_TYPE)
        animationOptions = AnimationOptions(name="RubberBand", durationMs=C_SIDEBAR_ANIMATION_MS)

        sideBar: SideBar = SideBar(
            icons={
                eSideBarState.Expanded: collapsePath,
                eSideBarState.Collapsed: expandPath,
            },
            title=self._title,
            initialState=eSideBarState.Expanded,
            options=sideBarOptions,
            animationOptions=animationOptions,
        )

        return sideBar

        pages = buildNavigationPages()
        pageIndex: Dict[str, int] = {}
        for key, page in pages.items():
            idx = stack.addWidget(page)
            pageIndex[key] = idx

        if PAGE_DASHBOARD in pageIndex:
            stack.setCurrentIndex(pageIndex[PAGE_DASHBOARD])

        # menu, settings = buildSideBarMenu()
        
                    # menu.itemClicked.connect(self._onNavItemClicked)
                    # settings.clicked.connect(self._onNavItemClicked)

        self._sigDevicesReady.connect(self._onDevicesReadyUi)
        self._sigDeviceAdded.connect(self._onDeviceAddedUi)
        self._sigDeviceRemoved.connect(self._onDeviceRemovedUi)
        self._bindDeviceManager(self._deviceManager)

    def _wBuildMenu(self) -> None:
        sideBar: SideBar = self._sideBar
        menu, settings = buildSideBarMenu()        
        sideBar.setContent(menu)
        sideBar.setFooter(settings)

    def _wInitializeUI(self) -> None:                
        debug("[WorkSpace] _wInitializeUI ENTER")
        super()._wInitializeUI()
        try:
            sideBar = self._buildSideBar()

            stack: QStackedWidget = QStackedWidget()
            stack.setSizePolicy(QSPolicy.Expanding, QSPolicy.Expanding)           
            
            layout: QBoxLayout = QBoxLayout(QBoxLayout.Direction.LeftToRight)
            layout.setSpacing(0)
            layout.setContentsMargins(0, 0, 0, 0)            
            layout.addWidget(sideBar)
            layout.addWidget(stack, 1)

            if hasattr(self, "_layout"): 
                self._layout = layout
                
            self.setLayout(layout)
            
            self._sideBar = sideBar
            self._stack = stack
            debug("[WorkSpace] _wInitializeUI EXIT ")

        except Exception as ex:
            error("[WorkSpace] _wInitializeUI FAIL", ex)

    def _onNavItemClicked(self, item: object) -> None:
        key = pageKeyOf(item)
        if key is None:
            if isinstance(item, SideBarMenuItem):
                debug(
                    f"[WorkSpace] nav skip caption={item.Caption!r} (no pageKey)"
                )
            return
        self.showPage(key)

    def showPage(self, key: str) -> bool:
        stack = self._stack
        index = self._pageIndex.get(key, None)
        if stack is None or index is None:
            warning(f"[WorkSpace] unknown page key={key!r}")
            return False
        stack.setCurrentIndex(index)
        page = self._pages.get(key)
        title = page.Title if page is not None else key
        debug(f"[WorkSpace] showPage key={key!r} title={title!r} index={index}")

        serial = serialFromPageKey(key)
        if serial is not None:
            # Must not be named _a* — @workflow auto-invokes those with no args.
            createTask(self._connectDeviceStream, serial, page)
        return True

    def detachAllStreams(self) -> None:
        """Unsubscribe all ON_FRAME UI handlers (call before widget teardown)."""
        mgr = self._deviceManager
        for serial, handler in list(self._frameHandlerBySerial.items()):
            emitter = mgr.getEmitter(serial) if mgr is not None else None
            if emitter is not None:
                try:
                    emitter.unsubscribe(C_ON_FRAME, handler)
                except Exception:
                    pass
        self._frameHandlerBySerial.clear()
        self._activeStreamSerial = None
        debug("[WorkSpace] detachAllStreams done")

    def _detachStream(self, serial: str) -> None:
        handler = self._frameHandlerBySerial.pop(serial, None)
        mgr = self._deviceManager
        if handler is None or mgr is None:
            return
        emitter = mgr.getEmitter(serial)
        if emitter is not None:
            try:
                emitter.unsubscribe(C_ON_FRAME, handler)
            except Exception:
                pass
        if self._activeStreamSerial == serial:
            self._activeStreamSerial = None

    async def _connectDeviceStream(self, serial: str, page: Optional[Page]) -> None:
        """Lazy-start global emitter and bind ON_FRAME to this page's Image."""
        mgr = self._deviceManager
        if mgr is None or page is None:
            return
        try:
            emitter = await mgr.ensureRunning(serial)
        except Exception as ex:
            error(f"[WorkSpace] ensureRunning failed serial={serial!r}", ex)
            error(f"[WorkSpace] traceback:\n{format_exc()}")
            return

        view = getattr(page, "_streamView", None)
        if view is None:
            warning(f"[WorkSpace] no stream view on page serial={serial!r}")
            return

        bridge = self._bridges.get(serial)
        if bridge is None:
            bridge = DeviceFrameBridge(self)
            bridge.frameReady.connect(
                lambda img, v=view: self._safeApplyFrame(v, img)
            )
            self._bridges[serial] = bridge
        else:
            try:
                bridge.frameReady.disconnect()
            except Exception:
                pass
            bridge.frameReady.connect(
                lambda img, v=view: self._safeApplyFrame(v, img)
            )

        self._detachStream(serial)

        def _onFrame(frame: object) -> None:
            try:
                if getattr(frame, "isConfig", False):
                    self._frameToQImage(frame, emitter)
                    return
                qimg = self._frameToQImage(frame, emitter)
                if qimg is None:
                    return
                try:
                    bridge.frameReady.emit(qimg)
                except RuntimeError:
                    pass
            except Exception:
                pass

        emitter.subscribe(C_ON_FRAME, _onFrame)
        self._frameHandlerBySerial[serial] = _onFrame
        self._activeStreamSerial = serial
        page._streamAttached = True  # type: ignore[attr-defined]
        debug(f"[WorkSpace] stream attached serial={serial!r}")

    @staticmethod
    def _safeApplyFrame(view: object, img: object) -> None:
        try:
            if isinstance(img, QImage):
                view.image = img  # type: ignore[attr-defined]
        except RuntimeError:
            pass
        except Exception as ex:
            warning(f"[WorkSpace] applyFrame failed: {ex}")

    @staticmethod
    def _frameToQImage(frame: object, emitter: SCRCPYEmitter) -> Optional[QImage]:
        try:
            decode = getattr(frame, "decode", None)
            if decode is None:
                return None
            codec = getattr(emitter, "_codecContext", None)
            if codec is None:
                return None
            vf = decode(codec, toGPU=False)
            if vf is None:
                return None
            if hasattr(vf, "to_ndarray"):
                import numpy as np

                arr = vf.to_ndarray(format="rgb24")
                if not isinstance(arr, np.ndarray):
                    return None
                h, w, _c = arr.shape
                qimg = QImage(
                    arr.data, w, h, 3 * w, QImage.Format.Format_RGB888
                )
                return qimg.copy()
            if hasattr(vf, "to_image"):
                pil = vf.to_image()
                data = pil.convert("RGB").tobytes()
                w, h = pil.size
                qimg = QImage(data, w, h, 3 * w, QImage.Format.Format_RGB888)
                return qimg.copy()
        except Exception:
            return None
        return None

    def _bindDeviceManager(self, mgr: Optional[deviceManager]) -> None:
        self._deviceManager = mgr
        if mgr is None:
            return
        mgr.subscribe(DEVICE_INITIALIZED_EVENT, self._onDevicesReadyEvent)
        mgr.subscribe(DEVICE_ADDED_EVENT, self._onDeviceAddedEvent)
        mgr.subscribe(DEVICE_REMOVED_EVENT, self._onDeviceRemovedEvent)
        debug("[WorkSpace] subscribed to deviceManager events")

    def _onDevicesReadyEvent(self, mgr: object) -> None:
        self._sigDevicesReady.emit(mgr)

    def _onDeviceAddedEvent(self, device: object) -> None:
        self._sigDeviceAdded.emit(device)

    def _onDeviceRemovedEvent(self, device: object) -> None:
        self._sigDeviceRemoved.emit(device)

    def _onDevicesReadyUi(self, mgr: object) -> None:
        try:
            devices = self._listDevices(mgr)
            debug(f"[WorkSpace] devices ready count={len(devices)}")
            self._syncDevicesList(devices)

        except Exception as ex:
            error("[WorkSpace] _onDevicesReadyUi FAIL", ex)

    def _onDeviceAddedUi(self, device: object) -> None:
        try:
            if not self._isDevice(device):
                return
            debug(f"[WorkSpace] device added id={device.id!r} name={device.name!r}")
            self._registerDevice(device)
            self._rebuildDevicesMenuLeaves()
            
        except Exception as ex:
            error("[WorkSpace] _onDeviceAddedUi FAIL", ex)
            error(f"[WorkSpace] traceback:\n{format_exc()}")

    def _onDeviceRemovedUi(self, device: object) -> None:
        try:
            if not self._isDevice(device):
                return
            serial = str(device.id)
            key = devicePageKeyFromId(serial)
            debug(f"[WorkSpace] device removed id={serial!r} key={key!r}")
            self._detachStream(serial)
            self._bridges.pop(serial, None)
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
        self._ensureDevicePage(key, title, serial=str(device.id))
        self._devicePageKeys.add(key)
        return key

    def _ensureDevicePage(
        self, key: str, title: str, serial: Optional[str] = None
    ) -> None:
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

        if serial is None:
            serial = serialFromPageKey(key) or title

        if key.startswith(C_DEVICE_KEY_PREFIX) and serial:
            page = buildDevicePage(key, title, serial)
        else:
            from ...UI.pages import buildBlankPage

            page = buildBlankPage(key, title, "Device")

        idx = stack.addWidget(page)
        self._pages[key] = page
        self._pageIndex[key] = idx
        debug(f"[WorkSpace] registered device page key={key!r} index={idx}")

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
        debug(f"[WorkSpace] unregistered device page key={key!r}")

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
        debug(
            f"[WorkSpace] rebuild devices menu "
            f"mgr_count={len(devices)} prior_children={len(header.Children)}"
        )

        header.clearChildren()

        if not devices:
            debug("[WorkSpace] devices menu -> empty (header only)")
            return

        for device in devices:
            if not self._isDevice(device):
                continue
            key = devicePageKeyFromId(str(device.id))
            caption = (device.name or "").strip() or str(device.id)
            leaf = header.addChild(caption)
            setPageKey(leaf, key)
            self._ensureDevicePage(key, caption, serial=str(device.id))

        header.Expanded = True
        captions = [c.Caption for c in header.Children]
        debug(
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
