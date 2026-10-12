# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Callable, List, Optional, Union

# ==================================================================================
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QBoxLayout, QSizePolicy, QWidget

# ==================================================================================
from jAGFx.workflow import workflow
from jAGQt.animations import RollAnimation

# ==================================================================================
from ....utilities import newLayout
from ...components import ComponentBase

# ==================================================================================
from .__sideBarItem import (
    IconPosition,
    ItemDisplayMode,
    ItemRole,
    SideBarItem,
    SideBarText,
)
from .__sideBarSeparator import SeparatorType, SideBarSeparator


# ==================================================================================
@workflow
class SideBarGroup(QWidget, ComponentBase):
    OBJECT_NAME = "W_SIDEBAR_GROUP"
    Toggled = Signal(bool)
    ItemClicked = Signal(object)

    def __init__(
        self, title: str = "", icon: Optional[Union[QIcon, QPixmap, str]] = None,
        iconSize: int = 20, depth: int = 0, collapsed: bool = False,
        animationDurationMs: int = 180, spacing: int = 2,
        *args, **kwargs,
    ) -> None:
        OBJNAME: str = kwargs.pop("objectName", self.OBJECT_NAME)
        super().__init__(objectName=OBJNAME, *args, **kwargs)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._collapsed: bool = bool(collapsed)
        self._iconSize: int = max(1, int(iconSize))
        self._depth: int = max(0, int(depth))
        self._childIconSize: int = max(1, self._iconSize - 2)
        self._animationDurationMs: int = max(0, int(animationDurationMs))
        self._sidebarCollapsed: bool = False
        self._items: List[SideBarItem] = []
        self._childGroups: List[SideBarGroup] = []

        self._title: str = title
        self._icon: Optional[Union[QIcon, QPixmap, str]] = icon
        self._spacing: int = max(0, int(spacing))

    def _wInitializeUI(self):
        title: str = self._title if self._title is not None else ""
        icon: Optional[Union[QIcon, QPixmap, str]] = self._icon
        spacing: int = self._spacing

        del self._title
        del self._icon
        del self._spacing

        header: SideBarItem = SideBarItem(
            text=title, icon=icon,
            displayMode=ItemDisplayMode.IconAndText,
            iconPosition=IconPosition.Left,
            iconSize=self._iconSize,
            depth=self._depth, role=ItemRole.Header,
            spacing=6
        )
        header.Clicked.connect(self._onHeaderClicked)

        body: QWidget = QWidget(self)
        body.setObjectName("W_SIDEBAR_GROUP_BODY")
        body.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        bodyLayout: QBoxLayout = newLayout(
            QBoxLayout, spacing=spacing, margins=(4, 0, 4, 4),
            direction=QBoxLayout.Direction.TopToBottom,
        )

        body.setLayout(bodyLayout)

        mainLayout: QBoxLayout = newLayout(
            QBoxLayout,
            spacing=0,
            margins=(0, 0, 0, 0),
            direction=QBoxLayout.Direction.TopToBottom,
        )        
        mainLayout.addWidget(header)
        mainLayout.addWidget(body)
        self.setLayout(mainLayout)

        self._header: SideBarItem = header
        self._body: QWidget = body        

        self._animation: RollAnimation = RollAnimation(
            target=self._body,
            durationMs=self._animationDurationMs,
            parent=self,
        )
        self._applyCollapsedState(animate=False)

    # ==================================================================================
    def AddItem(
        self,
        text: str = "",
        icon: Optional[Union[QIcon, QPixmap, str]] = None,
        displayMode: ItemDisplayMode = ItemDisplayMode.IconAndText,
        iconPosition: IconPosition = IconPosition.Left,
        iconSize: Optional[int] = None,
        callback: Optional[Callable] = None,
        id: Optional[str] = None,
    ) -> SideBarItem:
        lSize: int = iconSize if iconSize is not None else self._childIconSize
        lItem: SideBarItem = SideBarItem(
            text=text,
            icon=icon,
            displayMode=displayMode,
            iconPosition=iconPosition,
            iconSize=lSize,
            depth=self._depth + 1,
            role=ItemRole.Leaf,
            callback=callback,
            id=id,
            parent=self._body,
        )
        lItem.Clicked.connect(self._onChildItemClicked)
        self._bodyLayout.addWidget(lItem)
        self._items.append(lItem)
        if self._sidebarCollapsed:
            lItem.DisplayMode = ItemDisplayMode.IconOnly
        return lItem

    def AddGroup(
        self,
        title: str = "",
        icon: Optional[Union[QIcon, QPixmap, str]] = None,
        iconSize: Optional[int] = None,
        startCollapsed: bool = False,
    ) -> "SideBarGroup":
        lSize: int = iconSize if iconSize is not None else self._childIconSize
        lGroup: SideBarGroup = SideBarGroup(
            title=title,
            icon=icon,
            iconSize=lSize,
            depth=self._depth + 1,
            startCollapsed=startCollapsed,
            animationDurationMs=self._animationDurationMs,
            parent=self._body,
        )
        lGroup.ItemClicked.connect(self.ItemClicked.emit)
        self._bodyLayout.addWidget(lGroup)
        self._childGroups.append(lGroup)
        if self._sidebarCollapsed:
            lGroup.SetSidebarCollapsed(True)
        return lGroup

    def AddSeparator(
        self, separatorType: SeparatorType = SeparatorType.Line
    ) -> SideBarSeparator:
        lSep: SideBarSeparator = SideBarSeparator(
            separatorType=separatorType, parent=self._body
        )
        self._bodyLayout.addWidget(lSep)
        return lSep

    def AddStretch(self, stretch: int = 1) -> None:
        self._bodyLayout.addStretch(stretch)

    def Clear(self) -> None:
        self._items.clear()
        self._childGroups.clear()
        while self._bodyLayout.count():
            lItem = self._bodyLayout.takeAt(0)
            if lItem.widget():
                lItem.widget().setParent(None)
                lItem.widget().deleteLater()

    def Items(self) -> List[SideBarItem]:
        return list(self._items)

    def ChildGroups(self) -> List["SideBarGroup"]:
        return list(self._childGroups)

    def CollectItems(self) -> List[SideBarItem]:
        """Header + leaves + recursive nested group items."""
        lResult: List[SideBarItem] = [self._header]
        lResult.extend(self._items)
        for lGroup in self._childGroups:
            lResult.extend(lGroup.CollectItems())
        return lResult

    def FindAncestorHeaders(self, item: SideBarItem) -> List[SideBarItem]:
        """Return header chain from this group if *item* is under it."""
        if item is self._header:
            return [self._header]
        if item in self._items:
            return [self._header]
        for lGroup in self._childGroups:
            lChain = lGroup.FindAncestorHeaders(item)
            if lChain:
                return [self._header] + lChain
        return []

    def SetSidebarCollapsed(self, collapsed: bool) -> None:
        self._sidebarCollapsed = bool(collapsed)
        lMode = (
            ItemDisplayMode.IconOnly
            if self._sidebarCollapsed
            else ItemDisplayMode.IconAndText
        )
        self._header.DisplayMode = lMode
        for lItem in self._items:
            lItem.DisplayMode = lMode
        for lGroup in self._childGroups:
            lGroup.SetSidebarCollapsed(collapsed)
        if self._sidebarCollapsed:
            self.Collapse(animate=False)

    def Collapse(self, animate: bool = True) -> None:
        if self._collapsed:
            return
        self._collapsed = True
        self._applyCollapsedState(animate=animate)
        self.Toggled.emit(True)

    def Expand(self, animate: bool = True) -> None:
        if self._sidebarCollapsed:
            return
        if not self._collapsed:
            return
        self._collapsed = False
        self._applyCollapsedState(animate=animate)
        self.Toggled.emit(False)

    def Toggle(self, animate: bool = True) -> None:
        if self._collapsed:
            self.Expand(animate=animate)
        else:
            self.Collapse(animate=animate)

    @property
    def Collapsed(self) -> bool:
        return self._collapsed

    @Collapsed.setter
    def Collapsed(self, value: bool) -> None:
        if bool(value):
            self.Collapse()
        else:
            self.Expand()

    @property
    def HeaderWidget(self) -> SideBarItem:
        return self._header

    @property
    def BodyWidget(self) -> QWidget:
        return self._body

    @property
    def Depth(self) -> int:
        return self._depth

    def _onHeaderClicked(self, _item: SideBarItem) -> None:
        if self._sidebarCollapsed:
            self.ItemClicked.emit(self._header)
            return
        self.Toggle(animate=True)
        self.ItemClicked.emit(self._header)

    def _onChildItemClicked(self, item: SideBarItem) -> None:
        self.ItemClicked.emit(item)

    def _applyCollapsedState(self, animate: bool = True) -> None:
        if self._collapsed:
            lStart: int = self._body.height() if self._body.isVisible() else 0
            if not animate or self._animationDurationMs <= 0:
                self._body.setMaximumHeight(0)
                self._body.setVisible(False)
                return
            self._roll.SetRange(lStart, 0)
            self._roll.Start()
        else:
            self._body.setVisible(True)
            self._body.setMaximumHeight(16777215)
            lTarget: int = max(0, self._body.sizeHint().height())
            if not animate or self._animationDurationMs <= 0:
                self._body.setMaximumHeight(16777215)
                return
            self._body.setMaximumHeight(max(1, lTarget))
            self._roll.SetRange(0, lTarget)
            self._roll.Finished.connect(self._onRollExpandFinished)
            self._roll.Start()

    def _onRollExpandFinished(self) -> None:
        try:
            self._roll.Finished.disconnect(self._onRollExpandFinished)
        except (RuntimeError, TypeError):
            pass
        if not self._collapsed:
            self._body.setMaximumHeight(16777215)
