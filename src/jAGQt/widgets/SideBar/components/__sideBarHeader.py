# ==================================================================================
# src/jAGQt/widgets/SideBar/components/__sideBarHeader.py
# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QMouseEvent
from PySide6.QtWidgets import QBoxLayout, QSizePolicy, QStyle, QWidget

# ==================================================================================
from ....types.components import ComponentBase
from ....utilities import newLayout

# ==================================================================================
from .__sideBarIcon import SideBarIcon
from .__sideBarText import SideBarText


# ==================================================================================
class SideBarHeader(QWidget, ComponentBase):
    """Independent header region for the SideBar (title + optional collapse control)."""

    CollapseRequested = Signal()

    def __init__(
        self, title: str = "", icon: Optional[object] = None, iconSize: int = 20,
        showCollapseButton: bool = True, spacing: int = 8, parent: Optional[QWidget] = None,
        *args, **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)

        self.setObjectName("SideBarHeader")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._showCollapseButton: bool = showCollapseButton
        self._collapsed: bool = False
        self._collapseIconSize: int = max(14, min(iconSize, 18))

        self._iconWidget = SideBarIcon(icon=icon, iconSize=iconSize, parent=self)
        self._titleWidget = SideBarText(text=title, parent=self)
        self._titleWidget.setObjectName("SideBarHeaderTitle")

        self._collapseButton = SideBarIcon(
            icon=None,
            iconSize=self._collapseIconSize,
            parent=self,
        )
        self._collapseButton.setObjectName("SideBarHeaderCollapse")
        self._collapseButton.setCursor(Qt.CursorShape.PointingHandCursor)
        self._collapseButton.mousePressEvent = self._onCollapseClicked  # type: ignore

        self._layout: QBoxLayout = newLayout(
            QBoxLayout, spacing=spacing, margins=(8, 8, 9, 8)
        )
        self._layout.setDirection(QBoxLayout.Direction.LeftToRight)
        self.setLayout(self._layout)

        self._rebuild()
        self._refreshCollapseIcon()

    # ================================================================================== public API
    def SetTitle(self, title: str) -> None:
        self.Title = title

    def SetIcon(self, icon) -> None:
        self._iconWidget.SetIcon(icon)

    def SetCollapsed(self, collapsed: bool) -> None:
        lValue = bool(collapsed)
        if lValue == self._collapsed:
            return
        self._collapsed = lValue
        self._refreshCollapseIcon()

    # ================================================================================== properties
    @property
    def Title(self) -> str:
        return self._titleWidget.Text

    @Title.setter
    def Title(self, value: str) -> None:
        self._titleWidget.Text = value

    @property
    def ShowCollapseButton(self) -> bool:
        return self._showCollapseButton

    @ShowCollapseButton.setter
    def ShowCollapseButton(self, value: bool) -> None:
        if value == self._showCollapseButton: return
        self._showCollapseButton = bool(value)
        self._rebuild()

    @property
    def IconWidget(self) -> SideBarIcon:
        return self._iconWidget

    @property
    def TitleWidget(self) -> SideBarText:
        return self._titleWidget

    @property
    def CollapseButton(self) -> SideBarIcon:
        return self._collapseButton

    # ================================================================================== private
    def _standardIcon(self, standardPixmap: QStyle.StandardPixmap) -> QIcon:
        return self.style().standardIcon(standardPixmap)

    def _refreshCollapseIcon(self) -> None:
        if self._collapsed:
            lIcon = self._standardIcon(QStyle.StandardPixmap.SP_ArrowRight)
        else:
            lIcon = self._standardIcon(QStyle.StandardPixmap.SP_ArrowLeft)
        self._collapseButton.SetIcon(lIcon)

    def _rebuild(self) -> None:
        # Detach from layout only — keep parent so no top-level window flashes
        while self._layout.count():
            self._layout.takeAt(0)

        self._layout.addWidget(self._iconWidget)
        self._layout.addWidget(self._titleWidget, 1)

        if self._showCollapseButton:
            self._layout.addWidget(self._collapseButton)

    def _onCollapseClicked(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.CollapseRequested.emit()
