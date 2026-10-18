# ==================================================================================
from __future__ import annotations

# ==================================================================================
from traceback import format_exc
from typing import Dict, Optional, Union

# ==================================================================================
from PySide6.QtCore import QSize, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QSizePolicy

# ==================================================================================
from jAGFx.workflow import workflow

# ==================================================================================
from ...icon import StatefullIcon
from ...text import Description, Title
from ..__eSideBarState import eSideBarState
from .__sideBarItem import SideBarItem

# ==================================================================================
QSPolicy = QSizePolicy.Policy
C_ICON_SIZE = 32
C_COLLAPSED_WIDTH = 48
# ==================================================================================


# ==================================================================================
@workflow
class SideBarHeader(SideBarItem):
    OBJECT_NAME = "W_SIDEBAR_HEADER"

    stateChanged = Signal(object)  # eSideBarState

    def __init__(
        self,
        title: str,
        description: str,
        icons: Dict[eSideBarState, Optional[Union[QIcon, QPixmap, str]]],
        initialState: eSideBarState = eSideBarState.Expanded,
        *args,
        **kwargs,
    ) -> None:
        if icons is None or len(icons) == 0:
            raise ValueError("icons must not be None or empty")

        verbose(
            f"[SideBarHeader] __init__ ENTER title={title!r} "
            f"initialState={initialState!r}"
        )
        try:
            super().__init__(*args, **kwargs)
            self._titleText: str = title
            self._descriptionText: str = description
            self._icons: Dict[eSideBarState, Optional[Union[QIcon, QPixmap, str]]] = (
                dict(icons)
            )
            self._initialState: eSideBarState = initialState
            self._collapsedWidth: int = C_COLLAPSED_WIDTH
            self._iconSize: int = C_ICON_SIZE
            self._chromeCollapsed: bool = False
            self._expandedMargins = (8, 8, 8, 8)
        except Exception as ex:
            error("[SideBarHeader] __init__ FAIL", ex)
            error(f"[SideBarHeader] __init__ traceback:\n{format_exc()}")
            raise
        verbose(
            f"[SideBarHeader] __init__ EXIT objectName={self.objectName()!r}"
        )

    def _wInitializeUI(self) -> None:
        verbose("[SideBarHeader] _wInitializeUI ENTER")
        try:
            super()._wInitializeUI()

            titleText: str = self._titleText
            descriptionText: str = self._descriptionText
            icons = self._icons
            initialState: eSideBarState = self._initialState
            del self._titleText
            del self._descriptionText
            del self._icons
            del self._initialState

            iconWidget: StatefullIcon[eSideBarState] = StatefullIcon(
                icons=icons,
                objectName=f"{self.OBJECT_NAME}_ICON",
            )
            iconWidget.setFixedSize(QSize(C_ICON_SIZE, C_ICON_SIZE))
            iconWidget.setSizePolicy(QSPolicy.Fixed, QSPolicy.Fixed)
            if initialState in icons:
                iconWidget.state = initialState

            titleWidget: Title = Title(
                titleText, objectName=f"{self.OBJECT_NAME}_TITLE"
            )
            descriptionWidget: Description = Description(
                descriptionText,
                objectName=f"{self.OBJECT_NAME}_DESCRIPTION",
            )
            if not descriptionText:
                descriptionWidget.hide()

            self._addLeading(iconWidget)
            self._addTextWidget(titleWidget)
            self._addTextWidget(descriptionWidget)

            self._icon: StatefullIcon[eSideBarState] = iconWidget
            self._titleWidget: Title = titleWidget
            self._descriptionWidget: Description = descriptionWidget
            self._expandedMargins = (
                self._layout.contentsMargins().left(),
                self._layout.contentsMargins().top(),
                self._layout.contentsMargins().right(),
                self._layout.contentsMargins().bottom(),
            )

            iconWidget.stateChanged.connect(self._onIconStateChanged)
            verbose("[SideBarHeader] _wInitializeUI EXIT")
        except Exception as ex:
            error("[SideBarHeader] _wInitializeUI FAIL", ex)
            error(f"[SideBarHeader] _wInitializeUI traceback:\n{format_exc()}")
            raise

    def setChromeCollapsed(self, collapsed: bool) -> None:
        """Icon-only: hide text, center icon in collapsed rail width."""
        self._chromeCollapsed = bool(collapsed)
        if self._layout is None:
            return
        if self._chromeCollapsed:
            self._titleWidget.hide()
            self._descriptionWidget.hide()
            hPad = max(0, (self._collapsedWidth - self._iconSize) // 2)
            top = self._expandedMargins[1]
            bottom = self._expandedMargins[3]
            self._layout.setContentsMargins(hPad, top, hPad, bottom)
        else:
            self._layout.setContentsMargins(*self._expandedMargins)
            self._titleWidget.show()
            if self.Description.strip():
                self._descriptionWidget.show()
            else:
                self._descriptionWidget.hide()

    def setCollapsedWidth(self, width: int) -> None:
        self._collapsedWidth = int(width)
        if self._chromeCollapsed:
            self.setChromeCollapsed(True)

    def _onIconStateChanged(self, state: object) -> None:
        verbose(f"[SideBarHeader] stateChanged {state!r}")
        self.stateChanged.emit(state)

    @property
    def Title(self) -> str:
        return self._titleWidget.Text

    @Title.setter
    def Title(self, value: str) -> None:
        self._titleWidget.Text = value

    @property
    def Description(self) -> str:
        return self._descriptionWidget.Text

    @Description.setter
    def Description(self, value: str) -> None:
        self._descriptionWidget.Text = value
        if not self._chromeCollapsed:
            self._descriptionWidget.setVisible(bool(value.strip()) if value else False)

    @property
    def State(self) -> eSideBarState:
        return self._icon.state

    @State.setter
    def State(self, value: eSideBarState) -> None:
        self._icon.state = value

    def addIcon(
        self,
        state: eSideBarState,
        icon: Optional[Union[QIcon, QPixmap, str]] = None,
    ) -> None:
        self._icon.addIcon(state, icon)
