# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QMouseEvent
from PySide6.QtWidgets import QBoxLayout, QSizePolicy, QWidget

# ==================================================================================
from jAGFx.workflow import workflow
from jAGQt.icons import MakeBurgerIcon, MakeCloseIcon
from jAGQt.icons.animations import IconMorphAnimation

# ==================================================================================
from ....utilities import newLayout
from ...components import ComponentBase

# ==================================================================================
from .__sideBarIcon import SideBarIcon
from .__sideBarText import SideBarTitle


# ==================================================================================
@workflow
class SideBarHeader(QWidget, ComponentBase):
    OBJECT_NAME = "W_SIDEBAR_HEADER"
    CollapseRequested = Signal()
    def __init__(
        self, 
        title: str = "", iconSize: int = 20, spacing: int = 8,
        *args, **kwargs,
    ) -> None:
        OBJNAME: str = kwargs.pop("objectName", self.OBJECT_NAME)
        super().__init__(objectName=OBJNAME, *args, **kwargs)
        self._title: str = title
        self._iconSize: int = iconSize
        self._spacing: int = spacing

    def _wInitializeUI(self):
        title: str = self._title
        iconSize: int = max(1, int(self._iconSize))
        spacing: int = self._spacing

        del self._title
        del self._iconSize
        del self._spacing

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        collapsed: bool = False
        burgerIcon: QIcon = MakeBurgerIcon(iconSize)
        closeIcon: QIcon = MakeCloseIcon(iconSize)

        toggleIcon: SideBarIcon = SideBarIcon(icon=burgerIcon, iconSize=iconSize)
        toggleIcon.setCursor(Qt.CursorShape.PointingHandCursor)
        toggleIcon.mousePressEvent = self._onToggleClicked

        titleWidget: SideBarText = SideBarText(text=title)

        self._toggleIcon: SideBarIcon = toggleIcon
        self._titleWidget: SideBarText = SideBarText(text=title, parent=self)
        self._titleWidget.setObjectName("SideBarHeaderTitle")

        self._layout: QBoxLayout = newLayout(
            QBoxLayout,
            spacing=spacing,
            margins=(8, 8, 8, 8),
            direction=QBoxLayout.Direction.LeftToRight,
        )
        self.setLayout(self._layout)

        self._layout.addWidget(self._toggleIcon)
        self._layout.addWidget(self._titleWidget, 1)

        self._morph: IconMorphAnimation = IconMorphAnimation(
            target=self._toggleIcon,
            iconSize=self._iconSize,
            durationMs=160,
            parent=self,
        )

        self._applyCollapsedVisual(animate=False)

    # ==================================================================================
    def SetTitle(self, title: str) -> None:
        self.Title = title

    def SetCollapsed(self, collapsed: bool, animate: bool = True) -> None:
        lValue: bool = bool(collapsed)
        if lValue is self._collapsed:
            return
        self._collapsed = lValue
        self._applyCollapsedVisual(animate=animate)

    def SetIconSize(self, iconSize: int) -> None:
        self.IconSize = iconSize

    # ==================================================================================
    @property
    def Title(self) -> str:
        return self._titleWidget.Text

    @Title.setter
    def Title(self, value: str) -> None:
        self._titleWidget.Text = value

    @property
    def IconSize(self) -> int:
        return self._iconSize

    @IconSize.setter
    def IconSize(self, value: int) -> None:
        lSize: int = max(1, int(value))
        if lSize == self._iconSize:
            return
        self._iconSize = lSize
        self._burgerIcon = MakeBurgerIcon(lSize)
        self._closeIcon = MakeCloseIcon(lSize)
        self._toggleIcon.IconSize = lSize
        self._morph.SetIconSize(lSize)
        self._refreshToggleIcon(animate=False)

    @property
    def Collapsed(self) -> bool:
        return self._collapsed

    @Collapsed.setter
    def Collapsed(self, value: bool) -> None:
        self.SetCollapsed(value)

    # ==================================================================================
    def _refreshToggleIcon(self, animate: bool = True) -> None:
        lStart: QIcon = self._closeIcon if not self._collapsed else self._burgerIcon
        lEnd: QIcon = self._closeIcon if self._collapsed else self._burgerIcon
        if animate:
            self._morph.SetIcons(lStart, lEnd)
            self._morph.Start()
        else:
            self._toggleIcon.SetIcon(lEnd)

    def _applyCollapsedVisual(self, animate: bool = True) -> None:
        self._refreshToggleIcon(animate=animate)
        self._titleWidget.setVisible(not self._collapsed)
        self.setProperty("collapsed", "true" if self._collapsed else "false")
        self.style().unpolish(self)
        self.style().polish(self)

    def _onToggleClicked(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.CollapseRequested.emit()
