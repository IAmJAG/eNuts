# ==================================================================================
from __future__ import annotations

# ==================================================================================
from traceback import format_exc
from typing import Dict, Optional

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QBoxLayout, QSizePolicy, QStackedWidget, QWidget

# ==================================================================================
from jAGFx.workflow import workflow
from jAGQt.options import AnimationOptions, SideBarOptions
from jAGQt.widgets.components import ComponentBase, ObjectName
from jAGQt.widgets.page import Page
from jAGQt.widgets.sideBar import SideBar, SideBarMenuItem, eSideBarState
from utilities.io import getICONPath

# ==================================================================================
from ...UI.navigation import buildSmokeTestSideBarMenu, pageKeyOf
from ...UI.pages import PAGE_KEYS, buildSmokeTestPages
from ...UI.pages.__smokePages import PAGE_DASHBOARD

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

    def __init__(self: QWidget, *args, **kwargs) -> None:
        verbose("[WorkSpace] __init__ ENTER")
        try:
            super().__init__(*args, **kwargs)
            self._sideBar: Optional[SideBar] = None
            self._stack: Optional[QStackedWidget] = None
            self._pages: Dict[str, Page] = {}
            self._pageIndex: Dict[str, int] = {}
        except Exception as ex:
            error("[WorkSpace] __init__ FAIL", ex)
            error(f"[WorkSpace] __init__ traceback:\n{format_exc()}")
            raise

        verbose(f"[WorkSpace] __init__ EXIT objectName={self.objectName()!r}")

    def _wInitializeUI(self: QWidget) -> None:
        verbose("[WorkSpace] _wInitializeUI ENTER")
        try:
            self.setAttribute(StyleBackground, True)
            self.setStyleSheet("background-color: #1e1e1e;")

            expandPath: str = getICONPath("expand.png")
            collapsePath: str = getICONPath("collapse.png")
            verbose(
                f"[WorkSpace] SideBar icons expand={expandPath!r} collapse={collapsePath!r}"
            )

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

            menu, settings = buildSmokeTestSideBarMenu()
            sideBar.Content = menu
            sideBar.Footer = settings

            stack: QStackedWidget = QStackedWidget()
            stack.setObjectName("W_WORKSPACE_STACK")
            stack.setStyleSheet("background-color: #252526;")
            stack.setSizePolicy(QSPolicy.Expanding, QSPolicy.Expanding)

            pages = buildSmokeTestPages()
            pageIndex: Dict[str, int] = {}
            for key in PAGE_KEYS:
                page = pages[key]
                idx = stack.addWidget(page)
                pageIndex[key] = idx
                verbose(f"[WorkSpace] stack add page key={key!r} index={idx}")

            # Default landing page
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

            verbose(
                f"[WorkSpace] _wInitializeUI EXIT "
                f"sideBar.width={sideBar.width()} pages={list(pageIndex.keys())}"
            )
        except Exception as ex:
            error("[WorkSpace] _wInitializeUI FAIL", ex)
            error(f"[WorkSpace] _wInitializeUI traceback:\n{format_exc()}")
            raise

    def _onNavItemClicked(self, item: object) -> None:
        key = pageKeyOf(item)
        if key is None:
            # Headers without a pageKey (Devices, Tools) only expand/collapse.
            if isinstance(item, SideBarMenuItem):
                verbose(
                    f"[WorkSpace] nav skip caption={item.Caption!r} (no pageKey)"
                )
            return
        self.showPage(key)

    def showPage(self, key: str) -> bool:
        """Switch the stack to the page registered under ``key``."""
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

    @property
    def SideBar(self) -> Optional[SideBar]:
        return self._sideBar

    @property
    def Stack(self) -> Optional[QStackedWidget]:
        return self._stack

    @property
    def Pages(self) -> Dict[str, Page]:
        return dict(self._pages)
