# ==================================================================================
from __future__ import annotations

# ==================================================================================
from traceback import format_exc
from typing import Dict, Optional, Union

# ==================================================================================
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QBoxLayout, QSizePolicy, QWidget

# ==================================================================================
from jAGFx.workflow import workflow

# ==================================================================================
from ...utilities import newLayout
from ..components import ComponentBase, ObjectName
from .__eSideBarState import eSideBarState
from .components import SideBarHeader

# ==================================================================================
QSPolicy = QSizePolicy.Policy
C_EXPANDED_WIDTH = 200
C_COLLAPSED_WIDTH = 48
# ==================================================================================


# ==================================================================================
@workflow
class SideBar(ComponentBase, ObjectName, QWidget):
    OBJECT_NAME = "W_SIDEBAR"

    def __init__(
        self,
        icons: Dict[eSideBarState, Optional[Union[QIcon, QPixmap, str]]],
        title: str = "",
        description: str = "",
        initialState: eSideBarState = eSideBarState.Expanded,
        *args,
        **kwargs,
    ) -> None:
        if icons is None or len(icons) == 0:
            raise ValueError("icons must not be None or empty")

        verbose(
            f"[SideBar] __init__ ENTER title={title!r} "
            f"initialState={initialState!r} iconKeys={list(icons.keys())!r}"
        )
        try:
            super().__init__(*args, **kwargs)
            self._titleText: str = title
            self._descriptionText: str = description
            self._icons: Dict[eSideBarState, Optional[Union[QIcon, QPixmap, str]]] = (
                dict(icons)
            )
            self._initialState: eSideBarState = initialState
            self._sidebarState: eSideBarState = initialState
        except Exception as ex:
            error("[SideBar] __init__ FAIL", ex)
            error(f"[SideBar] __init__ traceback:\n{format_exc()}")
            raise
        verbose(f"[SideBar] __init__ EXIT objectName={self.objectName()!r}")

    def _wInitializeUI(self) -> None:
        verbose("[SideBar] _wInitializeUI ENTER")
        try:
            self.setSizePolicy(QSPolicy.Fixed, QSPolicy.Expanding)
            self.setStyleSheet(
                "background-color: #333337; border-right: 1px solid #3c3c3c;"
            )

            titleText: str = self._titleText
            descriptionText: str = self._descriptionText
            icons = self._icons
            initialState: eSideBarState = self._initialState
            del self._titleText
            del self._descriptionText
            del self._icons
            del self._initialState

            verbose("[SideBar] creating SideBarHeader")
            header: SideBarHeader = SideBarHeader(
                title=titleText,
                description=descriptionText,
                icons=icons,
                initialState=initialState,
            )
            verbose(
                f"[SideBar] SideBarHeader created objectName={header.objectName()!r}"
            )

            outerLayout: QBoxLayout = newLayout(
                QBoxLayout,
                spacing=0,
                margins=(0, 0, 0, 0),
                direction=QBoxLayout.Direction.TopToBottom,
            )
            outerLayout.addWidget(header, stretch=0)
            outerLayout.addStretch(1)

            self.setLayout(outerLayout)
            self._layout: QBoxLayout = outerLayout
            self._header: SideBarHeader = header
            self._sidebarState = initialState

            header.stateChanged.connect(self._onHeaderStateChanged)
            self._applySideBarState(initialState)

            verbose(
                f"[SideBar] _wInitializeUI EXIT "
                f"fixedWidth={self.width()} "
                f"sizePolicy={self.sizePolicy().horizontalPolicy()}"
            )
        except Exception as ex:
            error("[SideBar] _wInitializeUI FAIL", ex)
            error(f"[SideBar] _wInitializeUI traceback:\n{format_exc()}")
            raise

    def _onHeaderStateChanged(self, state: object) -> None:
        if not isinstance(state, eSideBarState):
            warning(f"[SideBar] ignoring non-eSideBarState: {state!r}")
            return
        verbose(f"[SideBar] header stateChanged -> {state!r}")
        self._applySideBarState(state)

    def _applySideBarState(self, state: eSideBarState) -> None:
        self._sidebarState = state
        header = self._header

        if state is eSideBarState.Collapsed:
            self.setFixedWidth(C_COLLAPSED_WIDTH)
            header._titleWidget.hide()
            header._descriptionWidget.hide()
        else:
            self.setFixedWidth(C_EXPANDED_WIDTH)
            header._titleWidget.show()
            if header.Description.strip():
                header._descriptionWidget.show()
            else:
                header._descriptionWidget.hide()

        self.updateGeometry()

    # ==================================================================================
    @property
    def Header(self) -> SideBarHeader:
        return self._header

    @property
    def Title(self) -> str:
        return self._header.Title

    @Title.setter
    def Title(self, value: str) -> None:
        self._header.Title = value

    @property
    def Description(self) -> str:
        return self._header.Description

    @Description.setter
    def Description(self, value: str) -> None:
        self._header.Description = value

    @property
    def State(self) -> eSideBarState:
        return self._sidebarState

    @State.setter
    def State(self, value: eSideBarState) -> None:
        if value == self._sidebarState and self._header.State == value:
            return
        # Drive through header/icon so wipe + stateChanged fire
        self._header.State = value
