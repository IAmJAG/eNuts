# ==================================================================================
from __future__ import annotations

# ==================================================================================
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
# ==================================================================================


# ==================================================================================
@workflow
class SideBar(ComponentBase, ObjectName, QWidget):
    OBJECT_NAME = "W_SIDEBAR"

    def __init__(
        self,
        title: str = "",
        description: str = "",
        icons: Dict[eSideBarState, Optional[Union[QIcon, QPixmap, str]]] = None,
        initialState: eSideBarState = eSideBarState.Expanded,
        *args,
        **kwargs,
    ) -> None:
        if icons is None or len(icons) == 0:
            raise ValueError("icons must not be None or empty")

        verbose("[SideBar] __init__ ENTER")
        super().__init__(*args, **kwargs)
        self._titleText: str = title
        self._descriptionText: str = description
        self._icons: Dict[eSideBarState, Optional[Union[QIcon, QPixmap, str]]] = dict(
            icons
        )
        self._initialState: eSideBarState = initialState
        verbose(f"[SideBar] __init__ EXIT objectName={self.objectName()!r}")

    def _wInitializeUI(self) -> None:
        verbose("[SideBar] _wInitializeUI ENTER")
        self.setSizePolicy(QSPolicy.Fixed, QSPolicy.Expanding)
        # DEV visibility: fixed width + solid background so the sidebar is obvious
        self.setFixedWidth(200)
        self.setStyleSheet("background-color: #333337; border-right: 1px solid #3c3c3c;")

        titleText: str = self._titleText
        descriptionText: str = self._descriptionText
        icons = self._icons
        initialState: eSideBarState = self._initialState
        del self._titleText
        del self._descriptionText
        del self._icons
        del self._initialState

        header: SideBarHeader = SideBarHeader(
            title=titleText,
            description=descriptionText,
            icons=icons,
            initialState=initialState,
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

        verbose(
            f"[SideBar] _wInitializeUI EXIT "
            f"fixedWidth={self.width()} sizePolicy={self.sizePolicy().horizontalPolicy()}"
        )

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
        return self._header.State

    @State.setter
    def State(self, value: eSideBarState) -> None:
        self._header.State = value
