# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Callable, List, Optional, Union

# ==================================================================================
from PySide6.QtCore import QPointF, Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QBoxLayout, QSizePolicy, QWidget

# ==================================================================================
from jAGQt.animations import LightningShootAnimation, RubberBandAnimation
from jAGQt.types import DockPosition

# ==================================================================================
from ...utilities import newLayout
from ..components import ComponentBase

# ==================================================================================
from .__options import sideBarConfig
from .components import (
    ItemDisplayMode,
    ItemRole,
    SeparatorType,
    SideBarContent,
    SideBarDockControl,
    SideBarGroup,
    SideBarHeader,
    SideBarItem,
    SideBarSeparator,
)


# ==================================================================================
class SideBar(QWidget, ComponentBase):
    CollapseRequested = Signal()
    CollapsedChanged = Signal(bool)
    DockSideChanged = Signal(object)
    ItemClicked = Signal(object)

    def __init__(
        self, title: str = "", config: Optional[sideBarConfig] = None,
        parent: Optional[QWidget] = None, *args, **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)
        self._config: sideBarConfig = config if config is not None else sideBarConfig()
        self._collapsed: bool = bool(self._config.startCollapsed)
        self._dockPosition: DockPosition = self._config.dockPosition
        self._activeItem: Optional[SideBarItem] = None
        self._groups: List[SideBarGroup] = []
        self._rootItems: List[SideBarItem] = []
        self._useLightningOnDock: bool = True
        self._dockAnimating: bool = False
        self._pendingDock: Optional[DockPosition] = None

        self.setObjectName("SideBar")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        expanded: int = self._config.expandedWidth
        collapsed: int = self._config.collapsedWidth
        self._expandedWidth: int = expanded
        self._collapsedWidth: int = collapsed

        initial: int = collapsed if self._collapsed else expanded
        self.setFixedWidth(initial)
        self.setMinimumWidth(initial)
        self.setMaximumWidth(initial)

        self._layout: QBoxLayout = newLayout(
            QBoxLayout,spacing=0, margins=(0, 0, 0, 0),
            direction=QBoxLayout.Direction.TopToBottom,
        )
        self.setLayout(self._layout)

        self._header: SideBarHeader = SideBarHeader(
            title=title, iconSize=self._config.iconSize,
        )
        self._header.CollapseRequested.connect(self._onHeaderCollapseRequested)

        self._content: SideBarContent = SideBarContent(parent=self)
        lDockIconSize: int = max(12, min(self._config.iconSize, 18))
        self._dockControl: SideBarDockControl = SideBarDockControl(
            dockPosition=self._dockPosition, iconSize=lDockIconSize,
        )
        self._dockControl.DockFlipRequested.connect(self._onDockFlipRequested)

        self._layout.addWidget(self._header)
        self._layout.addWidget(self._content, 1)
        self._layout.addWidget(self._dockControl)

        self._widthAnim: RubberBandAnimation = RubberBandAnimation(
            target=self, durationMs=max(self._config.animationDuration, 400),
            overshootPx=32, undershootPx=12
        )

        self._lightning: LightningShootAnimation = LightningShootAnimation(
            durationMs=720,
        )
        self._lightning.Finished.connect(self._onLightningFinished)

        self._applyDockProperty()
        if self._collapsed:
            self._header.SetCollapsed(True, animate=False)

    # ==================================================================================
    def AddItem(
        self, text: str = "", icon: Optional[Union[QIcon, QPixmap, str]] = None,
        displayMode: ItemDisplayMode = ItemDisplayMode.IconAndText,
        iconSize: Optional[int] = None, callback: Optional[Callable] = None,
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

        if lValue:
            self._widthAnim.SetRange(lStart, lEnd, overshootPx=14, undershootPx=6)
        else:
            self._widthAnim.SetRange(lStart, lEnd, overshootPx=36, undershootPx=14)
        self._widthAnim.Start()

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
        if self._dockAnimating:
            return

        if animate and self._useLightningOnDock:
            self._startDockLightning(position)
            return

        self._applyDockSide(position, animateArrow=animate)

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
        self.setMinimumWidth(lWidth)
        self.setMaximumWidth(lWidth)
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
    def _startDockLightning(self, position: DockPosition) -> None:
        lHost = self.window()
        if lHost is None:
            self._applyDockSide(position, animateArrow=True)
            return

        self._dockAnimating = True
        self._pendingDock = position

        # Source = current SideBar center in host coords
        lSrcGlobal = self.mapToGlobal(self.rect().center())
        lSrc = QPointF(lHost.mapFromGlobal(lSrcGlobal))
        lSize = QPointF(float(self.width()), float(max(self.height(), 120)))

        lMidY = float(lHost.height()) * 0.5
        lHalfW = float(self.width()) * 0.5
        lMargin = 8.0 + lHalfW
        if position is DockPosition.Right:
            lDst = QPointF(float(lHost.width()) - lMargin, lMidY)
        else:
            lDst = QPointF(lMargin, lMidY)

        self._lightning.SetPathPoints(
            lHost,
            lSrc,
            lDst,
            sourceSize=lSize,
            destSize=lSize,
            hideSource=True,
            onMidpoint=self._onLightningMidpoint,
        )
        self._lightning.Start()

    def _onLightningMidpoint(self) -> None:
        """Tentacle arrived — reparent SideBar to the destination edge while still hidden."""
        if self._pendingDock is None:
            return
        self._applyDockSide(self._pendingDock, animateArrow=True)

    def _onLightningFinished(self) -> None:
        self._dockAnimating = False
        self._pendingDock = None
        self.setVisible(True)

    def _applyDockSide(self, position: DockPosition, animateArrow: bool = True) -> None:
        self._dockPosition = position
        self._dockControl.SetDockPosition(position, animate=animateArrow)
        self._applyDockProperty()
        self.DockSideChanged.emit(position)

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
