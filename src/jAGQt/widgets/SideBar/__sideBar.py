# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Callable, List, Optional, Union

# ==================================================================================
from PySide6.QtCore import QPointF, Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QBoxLayout, QSizePolicy, QWidget

# ==================================================================================
from jAGQt.animations import DrawerAnimation, LightningShootAnimation, RubberBandAnimation
from jAGQt.types import DockPosition

# ==================================================================================
from ...utilities import newLayout
from ..components import ComponentBase

# ==================================================================================
from .__options import sideBarConfig
from .components import (
    ItemDisplayMode,
    ItemRole,
    SideBarContent,
    SideBarDockControl,
    SideBarGroup,
    SideBarHeader,
    SideBarItem,
    SideBarSeparator,
    SeparatorType,
)


# ==================================================================================
class SideBar(QWidget, ComponentBase):
    """Side bar: header, nested content, dock control.

    Collapse: drawer in / rubber-band out.
    Dock flip: transpose arrow + lightning across the window.
    Selection: one active item; ancestor headers selected (QSS by depth).
    """

    CollapseRequested = Signal()
    CollapsedChanged = Signal(bool)
    DockSideChanged = Signal(object)
    ItemClicked = Signal(object)

    def __init__(
        self,
        title: str = "",
        config: Optional[sideBarConfig] = None,
        parent: Optional[QWidget] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)

        self._config: sideBarConfig = config if config is not None else sideBarConfig()
        self._collapsed: bool = bool(self._config.startCollapsed)
        self._dockPosition: DockPosition = self._config.dockPosition
        self._activeItem: Optional[SideBarItem] = None
        self._groups: List[SideBarGroup] = []
        self._rootItems: List[SideBarItem] = []
        self._useLightningOnDock: bool = True

        self.setObjectName("SideBar")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        lExpanded: int = self._config.expandedWidth
        lCollapsed: int = self._config.collapsedWidth
        self._expandedWidth: int = lExpanded
        self._collapsedWidth: int = lCollapsed

        lInitial: int = lCollapsed if self._collapsed else lExpanded
        self.setFixedWidth(lInitial)
        self.setMinimumWidth(lCollapsed)
        self.setMaximumWidth(lExpanded)

        self._layout: QBoxLayout = newLayout(
            QBoxLayout,
            spacing=0,
            margins=(0, 0, 0, 0),
            direction=QBoxLayout.Direction.TopToBottom,
        )
        self.setLayout(self._layout)

        self._header: SideBarHeader = SideBarHeader(
            title=title,
            iconSize=self._config.iconSize,
            parent=self,
        )
        self._header.CollapseRequested.connect(self._onHeaderCollapseRequested)

        self._content: SideBarContent = SideBarContent(parent=self)

        lDockIconSize: int = max(12, min(self._config.iconSize, 18))
        self._dockControl: SideBarDockControl = SideBarDockControl(
            dockPosition=self._dockPosition,
            iconSize=lDockIconSize,
            parent=self,
        )
        self._dockControl.DockFlipRequested.connect(self._onDockFlipRequested)

        self._layout.addWidget(self._header)
        self._layout.addWidget(self._content, 1)
        self._layout.addWidget(self._dockControl)

        self._drawer: DrawerAnimation = DrawerAnimation(
            target=self,
            durationMs=self._config.animationDuration,
            parent=self,
        )
        self._rubber: RubberBandAnimation = RubberBandAnimation(
            target=self,
            durationMs=max(self._config.animationDuration, 280),
            overshootPx=16,
            parent=self,
        )
        self._lightning: LightningShootAnimation = LightningShootAnimation(
            durationMs=380,
            parent=self,
        )

        self._applyDockProperty()
        if self._collapsed:
            self._header.SetCollapsed(True, animate=False)

    # ==================================================================================
    def AddItem(
        self,
        text: str = "",
        icon: Optional[Union[QIcon, QPixmap, str]] = None,
        displayMode: ItemDisplayMode = ItemDisplayMode.IconAndText,
        iconSize: Optional[int] = None,
        callback: Optional[Callable] = None,
    ) -> SideBarItem:
        lSize: int = iconSize if iconSize is not None else self._config.iconSize
        lItem: SideBarItem = SideBarItem(
            text=text,
            icon=icon,
            displayMode=displayMode,
            iconSize=lSize,
            depth=0,
            role=ItemRole.Leaf,
            callback=callback,
            parent=self._content.Container,
        )
        lItem.Clicked.connect(self._onItemClicked)
        self._content.AddWidget(lItem)
        self._rootItems.append(lItem)
        if self._collapsed:
            lItem.DisplayMode = ItemDisplayMode.IconOnly
        return lItem

    def AddGroup(
        self,
        title: str = "",
        icon: Optional[Union[QIcon, QPixmap, str]] = None,
        iconSize: Optional[int] = None,
        startCollapsed: bool = False,
    ) -> SideBarGroup:
        lSize: int = iconSize if iconSize is not None else self._config.iconSize
        lGroup: SideBarGroup = SideBarGroup(
            title=title,
            icon=icon,
            iconSize=lSize,
            depth=0,
            startCollapsed=startCollapsed,
            animationDurationMs=self._config.animationDuration,
            parent=self._content.Container,
        )
        lGroup.ItemClicked.connect(self._onItemClicked)
        self._content.AddWidget(lGroup)
        self._groups.append(lGroup)
        if self._collapsed:
            lGroup.SetSidebarCollapsed(True)
        return lGroup

    def AddSeparator(
        self, separatorType: SeparatorType = SeparatorType.Line
    ) -> SideBarSeparator:
        lSep: SideBarSeparator = SideBarSeparator(
            separatorType=separatorType, parent=self._content.Container
        )
        self._content.AddWidget(lSep)
        return lSep

    def AddStretch(self, stretch: int = 1) -> None:
        self._content.AddStretch(stretch)

    def Clear(self) -> None:
        self._activeItem = None
        self._groups.clear()
        self._rootItems.clear()
        self._content.Clear()

    # ==================================================================================
    def SetTitle(self, title: str) -> None:
        self._header.SetTitle(title)

    def SetCollapsed(self, collapsed: bool) -> None:
        lValue: bool = bool(collapsed)
        if lValue is self._collapsed:
            return
        self._collapsed = lValue

        lStart: int = self.width()
        lEnd: int = self._collapsedWidth if lValue else self._expandedWidth
        self.setMaximumWidth(max(lStart, lEnd, self._expandedWidth))

        if lValue:
            self._drawer.SetRange(lStart, lEnd)
            self._drawer.Start()
        else:
            self._rubber.SetRange(lStart, lEnd, overshootPx=16)
            self._rubber.Start()

        self._header.SetCollapsed(lValue, animate=True)
        for lGroup in self._groups:
            lGroup.SetSidebarCollapsed(lValue)
        for lItem in self._rootItems:
            lItem.DisplayMode = (
                ItemDisplayMode.IconOnly if lValue else ItemDisplayMode.IconAndText
            )

        self.setProperty("collapsed", "true" if lValue else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        self.CollapsedChanged.emit(lValue)

    def ToggleCollapse(self) -> None:
        self.SetCollapsed(not self._collapsed)

    def SetDockSide(self, position: DockPosition, animate: bool = True) -> None:
        if position is self._dockPosition:
            return

        lRunLightning = bool(animate and self._useLightningOnDock)
        if lRunLightning:
            self._prepareDockLightning(position)

        self._dockPosition = position
        self._dockControl.SetDockPosition(position, animate=animate)
        self._applyDockProperty()
        self.DockSideChanged.emit(position)

        if lRunLightning:
            self._lightning.Start()

    def ToggleDockSide(self) -> None:
        lNext = (
            DockPosition.Right
            if self._dockPosition is DockPosition.Left
            else DockPosition.Left
        )
        self.SetDockSide(lNext)

    def SelectItem(self, item: SideBarItem) -> None:
        self._applySelection(item)

    def RestoreState(self, collapsed: bool, dockSide: str) -> None:
        """Apply persisted state without animation."""
        lDock = (
            DockPosition.Right
            if str(dockSide).lower() == "right"
            else DockPosition.Left
        )
        self._dockPosition = lDock
        self._dockControl.SetDockPosition(lDock, animate=False)
        self._applyDockProperty()

        lCollapsed = bool(collapsed)
        self._collapsed = lCollapsed
        lWidth = self._collapsedWidth if lCollapsed else self._expandedWidth
        self.setFixedWidth(lWidth)
        self.setMaximumWidth(self._expandedWidth)
        self._header.SetCollapsed(lCollapsed, animate=False)
        for lGroup in self._groups:
            lGroup.SetSidebarCollapsed(lCollapsed)
        for lItem in self._rootItems:
            lItem.DisplayMode = (
                ItemDisplayMode.IconOnly if lCollapsed else ItemDisplayMode.IconAndText
            )
        self.setProperty("collapsed", "true" if lCollapsed else "false")
        self.style().unpolish(self)
        self.style().polish(self)

    def ExportState(self) -> dict:
        return {
            "collapsed": self._collapsed,
            "dockSide": "right" if self._dockPosition is DockPosition.Right else "left",
        }

    # ==================================================================================
    @property
    def Config(self) -> sideBarConfig:
        return self._config

    @property
    def Title(self) -> str:
        return self._header.Title

    @Title.setter
    def Title(self, value: str) -> None:
        self._header.Title = value

    @property
    def Collapsed(self) -> bool:
        return self._collapsed

    @Collapsed.setter
    def Collapsed(self, value: bool) -> None:
        self.SetCollapsed(value)

    @property
    def DockSide(self) -> DockPosition:
        return self._dockPosition

    @DockSide.setter
    def DockSide(self, value: DockPosition) -> None:
        self.SetDockSide(value)

    # ==================================================================================
    def _prepareDockLightning(self, newSide: DockPosition) -> None:
        lHost = self.window()
        if lHost is None:
            return

        lMidY = float(lHost.height()) * 0.5
        lMargin = 24.0
        if self._dockPosition is DockPosition.Left:
            lStart = QPointF(lMargin, lMidY)
            lEnd = QPointF(float(lHost.width()) - lMargin, lMidY)
        else:
            lStart = QPointF(float(lHost.width()) - lMargin, lMidY)
            lEnd = QPointF(lMargin, lMidY)

        self._lightning.SetPathPoints(lHost, lStart, lEnd, affectOpacity=False)

    def _applyDockProperty(self) -> None:
        self.setProperty(
            "dockSide",
            "left" if self._dockPosition is DockPosition.Left else "right",
        )
        self.style().unpolish(self)
        self.style().polish(self)

    def _onHeaderCollapseRequested(self) -> None:
        self.ToggleCollapse()
        self.CollapseRequested.emit()

    def _onDockFlipRequested(self) -> None:
        self.ToggleDockSide()

    def _onItemClicked(self, item: SideBarItem) -> None:
        self._applySelection(item)
        self.ItemClicked.emit(item)

    def _allItems(self) -> List[SideBarItem]:
        lResult: List[SideBarItem] = list(self._rootItems)
        for lGroup in self._groups:
            lResult.extend(lGroup.CollectItems())
        return lResult

    def _applySelection(self, item: SideBarItem) -> None:
        for lItem in self._allItems():
            lItem.Active = False
            lItem.Selected = False

        item.Active = True
        self._activeItem = item

        for lGroup in self._groups:
            lChain = lGroup.FindAncestorHeaders(item)
            for lHeader in lChain:
                if lHeader is not item:
                    lHeader.Selected = True
