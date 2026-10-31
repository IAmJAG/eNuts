# ==================================================================================
from __future__ import annotations

# ==================================================================================
from traceback import format_exc
from typing import Dict, List, Optional, Set

# ==================================================================================
from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QImage
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
from ...types.interface.UI.windows import iENUTSWindow
from ...UI.navigation import (
    G_DEVICE_KEY_PREFIX,
    G_DEVICE_NONE,
    PAGE_DASHBOARD,
    PAGE_DEVICES,
    buildSideBarMenu,
    devicePageKeyFromId,
    pageKeyOf,
    serialFromPageKey,
    setPageKey,
)
from ...UI.pages import buildDevicePage, buildNavigationPages
from ...UI.pages.__devicePage import DeviceFrameBridge
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
@workflow("InitializeUI", "RegisterPages", "BuildMenu")
class WorkSpace(ComponentBase, ObjectName, QWidget):
    OBJECT_NAME = "W_WORKSPACE"
    def __init__(self,title: str = "eNuts", *args, **kwargs) -> None:        
        trace("ENTER")
        super().__init__(*args, **kwargs)        
        self._sideBar: Optional[SideBar] = None
        self._stack: Optional[QStackedWidget] = None
        self._pages: Dict[str, Page] = {}
        self._pageIndex: Dict[str, int] = {}        
        self._settings: Optional[QSettings] = None

        self._title: str = title
        trace("EXIT")

    @property
    def settings(self) -> QSettings:
        if self._settings is None:
            warning("Settings not yet initialized")

        return self._settings

    def _buildSideBar(self) -> SideBar:                
        try:
            trace("ENTER")
            settings: QSettings = self.settings

            expandPath: str = getICONPath("expand.png")
            collapsePath: str = getICONPath("collapse.png")

            sideBarOptions = SideBarOptions(animation = C_SIDEBAR_ANIMATION_TYPE)
            animationOptions = AnimationOptions(
                name = "RubberBand", durationMs = C_SIDEBAR_ANIMATION_MS
            )

            state: eSideBarState = settings.value("sideBarState", eSideBarState.Expanded)
            return SideBar(
                icons={
                    eSideBarState.Expanded: collapsePath,
                    eSideBarState.Collapsed: expandPath,
                },
                title = self._title,
                initialState = state,
                options = sideBarOptions,
                animationOptions = animationOptions,
            )

        except Exception as ex: 
            error("FAIL", ex)

        finally:
            trace("EXIT")

    def _wInitializeUI(self) -> None:
        try: 
            trace("ENTER")
            super()._wInitializeUI()
            
            parent: iENUTSWindow = self.Parent        
            if parent is not None: 
                qSettings = parent.settings
                
            if qSettings is None:
                qSettings = QSettings()
                warning("Settings invalid settings")
            
            self._settings: QSettings = qSettings
            
            sideBar: SideBar = self._buildSideBar()
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

        except Exception as ex: 
            error("FAIL", ex)

        finally:
            trace("EXIT")        

    def _wRegisterPages(self) -> None:
        try: 
            trace("ENTER")
            stack = self._stack
            if stack is None: 
                warning("Stack not built")
                return

            pages = buildNavigationPages()
            for key, page in pages.items():
                idx = stack.addWidget(page)
                self._pages[key] = page
                self._pageIndex[key] = idx
            
            if PAGE_DASHBOARD in self._pageIndex:
                stack.setCurrentIndex(self._pageIndex[PAGE_DASHBOARD])

        except Exception as ex:
            error("FAIL", ex)

        finally:
            trace("EXIT")

    def _wBuildMenu(self) -> None:
        try:
            trace("ENTER")

            sideBar = self._sideBar
            if sideBar is None:
                warning("SideBar not built")
                return

            menu, footer = buildSideBarMenu()
            sideBar.setContent(menu)
            sideBar.setFooter(footer)

            try:
                menu.itemClicked.connect(self._onNavItemClicked)

            except Exception as ex:
                error("menu.itemClicked connect failed", ex)

            if footer is not None:
                try:
                    footer.selectionRequested.connect(self._onNavItemClicked)

                except Exception as ex:
                    warning("footer.selectionRequested connect failed", ex)

            debug("attached content+footer")

        except Exception as ex:
            error("FAIL", ex)

        finally:
            trace("EXIT")

    def _onNavItemClicked(self, item: object) -> None:
        key = pageKeyOf(item)
        if key is None:
            if isinstance(item, SideBarMenuItem):
                debug(f"nav skip caption={item.Caption!r} (no pageKey)")
            return
        
        self.showPage(key)

    def showPage(self, key: str) -> bool:
        stack = self._stack
        index = self._pageIndex.get(key, None)

        if stack is None or index is None:
            warning(f"unknown page key={key!r}")
            return False
        
        stack.setCurrentIndex(index)
        page = self._pages.get(key, None)
        
        title = page.Title if page is not None else key
        debug(f"key={key!r} title={title!r} index={index}")
        return True

    @property
    def SideBar(self) -> SideBar:
        return self._sideBar

    @property
    def Stack(self) -> QStackedWidget:
        return self._stack

    @property
    def Pages(self) -> Dict[str, Page]:
        return dict(self._pages)