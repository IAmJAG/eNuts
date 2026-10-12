# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Callable, List, Optional, Union

# ==================================================================================
from PySide6.QtCore import QPointF, Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QBoxLayout, QSizePolicy, QWidget

from jAGFx.workflow import workflow

# ==================================================================================
from ...animations import LightningShootAnimation, RubberBandAnimation
from ...types.interface.animations import iAnimation
from ...utilities import newLayout
from ..components import ComponentBase
from .components import (
    SideBarContent,
    SideBarDockControl,
    SideBarGroup,
    SideBarHeader,
    SideBarItem,
    SideBarItemSeparator,
)
from .types import (
    SideBarDockPosition,
    SideBarItemDisplayMode,
    SideBarItemRole,
    SideBarItemSeparatorType,
    sideBarConfig,
)


# ==================================================================================
@workflow
class SideBar(QWidget, ComponentBase):
    OBJECT_NAME = "W_SIDEBAR"
    CollapseRequested = Signal()
    CollapsedChanged = Signal(bool)
    DockSideChanged = Signal(object)
    ItemClicked = Signal(object)

    def __init__(
        self, title: str = "", config: Optional[sideBarConfig] = None, *args, **kwargs,
    ) -> None:
        OBJNAME: str = kwargs.pop("objectName", self.OBJECT_NAME)
        super().__init__(objectName=OBJNAME, *args, **kwargs)
        self._title: str = title

        self._config: sideBarConfig = config if config is not None else sideBarConfig()

        self._activeItem: Optional[SideBarItem] = None
        self._groups: List[SideBarGroup] = []
        self._rootItems: List[SideBarItem] = []     

        self._dockPosition: SideBarDockPosition = self.config.dockPosition   

    def _wInitializeUI(self) -> None:
        title: str = self._title

        del self._title

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        expanded: int = self._config.expandedWidth
        collapsed: int = self._config.collapsedWidth
        
        initial: int = collapsed if self._config.isCollapsed else expanded
        self.setFixedWidth(initial)
        self.setMinimumWidth(initial)
        self.setMaximumWidth(initial)

        header: SideBarHeader = SideBarHeader(title=title, iconSize=self.config.iconSize,)
        content: SideBarContent = SideBarContent()
        dockControl: SideBarDockControl = SideBarDockControl()

        mainLayout: QBoxLayout = newLayout(QBoxLayout, spacing=0, margins=0)
        mainLayout.setDirection(QBoxLayout.Direction.TopToBottom)

        mainLayout.addWidget(header)        
        mainLayout.addWidget(content)
        mainLayout.addWidget(dockControl)
        self.setLayout(mainLayout)

        self._header: SideBarHeader = header
        self._content: SideBarContent = content
        self._dockControl: SideBarDockControl = dockControl

        self._widthAnimation: iAnimation = RubberBandAnimation(
            target=self, durationMs=max(self._config.animationDuration, 400),
            overshootPx=32, undershootPx=12,
        )
        self._switchDockAnimation: iAnimation = LightningShootAnimation(durationMs=720)

        self._xapplyDockProperty()
        if self.config.isCollapsed:
            self._header._setCollapsed(True, animate=False) # TODO: Fix. unintentionally used private method

    @property
    def config(self) -> sideBarConfig:
        return self._config

    def _xapplyDockProperty(self) -> None:
        strPosition: str = (
            "left" if self._dockPosition is SideBarDockPosition.Left else "right"
        )
        self.setProperty("dockSide", strPosition)
        self.style().unpolish(self)
        self.style().polish(self)

    # ==================================================================================
    def AddItem(
        self, text: str = "", icon: Optional[Union[QIcon, QPixmap, str]] = None,
        displayMode: SideBarItemDisplayMode = SideBarItemDisplayMode.IconAndText,
        iconSize: Optional[int] = None, callback: Optional[Callable] = None,
        id: Optional[str] = None,
    ) -> SideBarItem:
        lSize: int = iconSize if iconSize is not None else self._config.iconSize
        lItem: SideBarItem = SideBarItem(
            text=text, icon=icon, displayMode=displayMode,
            iconSize=lSize, depth=0, role=SideBarItemRole.Leaf,
            callback=callback, id=id,
        )
        lItem.Clicked.connect(self._onItemClicked)
        self._content.addWidget(lItem)
        self._rootItems.append(lItem)
        if self.config.isCollapsed: lItem.displayMode = SideBarItemDisplayMode.IconOnly
        return lItem

    def AddGroup(
        self, title: str = "", icon: Optional[Union[QIcon, QPixmap, str]] = None,
        iconSize: Optional[int] = None, isCollapsed: bool = False,
    ) -> SideBarGroup:
        lSize: int = iconSize if iconSize is not None else self._config.iconSize
        lGroup: SideBarGroup = SideBarGroup(
            title=title, icon=icon, iconSize=lSize, depth=0,
            isCollapsed=isCollapsed, animationDurationMs=self._config.animationDuration
        )
        lGroup.ItemClicked.connect(self._onItemClicked)
        self._content.addWidget(lGroup)
        self._groups.append(lGroup)
        if self.config.isCollapsed:
            lGroup.SetSidebarCollapsed(True)
        return lGroup

    def AddSeparator(self, separatorType: SideBarItemSeparatorType = SideBarItemSeparatorType.Line) -> SideBarItemSeparator:
        lSep: SideBarItemSeparator = SideBarItemSeparator(separatorType=separatorType)
        self._content.addWidget(lSep)
        return lSep

    def AddStretch(self, stretch: int = 1) -> None:
        self._content.addStretch(stretch)

    def Clear(self) -> None:
        self._activeItem = None
        self._groups.clear()
        self._rootItems.clear()
        self._content.Clear()

    # ==================================================================================
    def setTitle(self, title: str) -> None:
        self._header.SetTitle(title)

    def setCollapsed(self, collapsed: bool) -> None:
        lValue: bool = bool(collapsed)
        if lValue is self._collapsed:
            return
        self._collapsed = lValue

        lStart: int = self.width()
        lEnd: int = self.config.collapsedWidth if lValue else self.config.expandedWidth

        if lValue:
            self._widthAnimation.setRange(lStart, lEnd, overshootPx=14, undershootPx=6)
        else:
            self._widthAnimation.setRange(lStart, lEnd, overshootPx=36, undershootPx=14)

        self._widthAnimation.start()

        self._header._setCollapsed(lValue, animate=True)
        for lGroup in self._groups:
            lGroup.setSidebarCollapsed(lValue)

        for lItem in self._rootItems:
            lItem.displayMode = (
                SideBarItemDisplayMode.IconOnly if lValue else SideBarItemDisplayMode.IconAndText
            )

        self.setProperty("collapsed", "true" if lValue else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        self.CollapsedChanged.emit(lValue)

    def toggleCollapse(self) -> None:
        self.setCollapsed(not self._collapsed)

    def setDockSide(self, position: SideBarDockPosition, animate: bool = True) -> None:
        if position is self._dockPosition: return
        if self._dockAnimating: return
        self._startDockLightning(position)        
        self._xapplyDockSide(position, animateArrow=animate)

    def toggleDockSide(self) -> None:
        lNext = (
            SideBarDockPosition.Right
            if self._dockPosition is SideBarDockPosition.Left
            else SideBarDockPosition.Left
        )
        self.setDockSide(lNext)

    def selectItem(self, item: SideBarItem) -> None:
        self._xapplySelection(item)

    def restoreState(self, collapsed: bool, dockSide: str) -> None:
        lDock = (
            SideBarDockPosition.Right
            if str(dockSide).lower() == "right"
            else SideBarDockPosition.Left
        )
        self._dockPosition = lDock
        self._dockControl.setDockPosition(lDock, animate=False)
        self._xapplyDockProperty()

        lCollapsed = bool(collapsed)
        self.config.isCollapsed = lCollapsed

        lWidth = self.config.collapsedWidth if lCollapsed else self.config.expandedWidth
        self.setFixedWidth(lWidth)
        self.setMinimumWidth(lWidth)
        self.setMaximumWidth(lWidth)

        self._header._setCollapsed(lCollapsed, animate=False)
        for lGroup in self._groups: lGroup.setSidebarCollapsed(lCollapsed)
        for lItem in self._rootItems:
            lItem.displayMode = (
                SideBarItemDisplayMode.IconOnly if lCollapsed else SideBarItemDisplayMode.IconAndText
            )
        self.setProperty("collapsed", "true" if lCollapsed else "false")
        self.style().unpolish(self)
        self.style().polish(self)

    def ExportState(self) -> dict:
        return {
            "collapsed": self._collapsed,
            "dockSide": "right" if self._dockPosition is SideBarDockPosition.Right else "left",
        }

    # ==================================================================================
    @property
    def Config(self) -> sideBarConfig:
        return self._config

    @property
    def Title(self) -> str:
        return self._header.title

    @Title.setter
    def Title(self, value: str) -> None:
        self._header.title = value

    @property
    def Collapsed(self) -> bool:
        return self._collapsed

    @Collapsed.setter
    def Collapsed(self, value: bool) -> None:
        self.setCollapsed(value)

    @property
    def DockSide(self) -> SideBarDockPosition:
        return self._dockPosition

    @DockSide.setter
    def DockSide(self, value: SideBarDockPosition) -> None:
        self.setDockSide(value)

    # ==================================================================================
    def _startDockLightning(self, position: SideBarDockPosition) -> None:
        lHost = self.window()
        if lHost is None:
            self._xapplyDockSide(position, animateArrow=True)
            return

        self._dockAnimating = True
        self._pendingDock = position

        lSrcGlobal = self.mapToGlobal(self.rect().center())
        lSrc = QPointF(lHost.mapFromGlobal(lSrcGlobal))
        lSize = QPointF(float(self.width()), float(max(self.height(), 120)))

        lMidY = float(lHost.height()) * 0.5
        lHalfW = float(self.width()) * 0.5
        lMargin = 8.0 + lHalfW
        if position is SideBarDockPosition.Right:
            lDst = QPointF(float(lHost.width()) - lMargin, lMidY)
        else:
            lDst = QPointF(lMargin, lMidY)

        self._switchDockAnimation.SetPathPoints(
            lHost, lSrc, lDst, sourceSize=lSize,
            destSize=lSize, hideSource=True,
            onMidpoint=self._onLightningMidpoint,
        )
        self._switchDockAnimation.start()

    def _onLightningMidpoint(self) -> None:
        if self._pendingDock is None: return
        self._xapplyDockSide(self._pendingDock, animateArrow=True)

    def _onLightningFinished(self) -> None:
        self._dockAnimating = False
        self._pendingDock = None
        self.setVisible(True)

    def _xapplyDockSide(self, position: SideBarDockPosition, animateArrow: bool = True) -> None:
        self._dockPosition = position
        self._dockControl.setDockPosition(position, animate=animateArrow)
        self._xapplyDockProperty()
        self.DockSideChanged.emit(position)

    def _xapplyDockProperty(self) -> None:
        self.setProperty(
            "dockSide",
            "left" if self._dockPosition is SideBarDockPosition.Left else "right",
        )
        self.style().unpolish(self)
        self.style().polish(self)

    def _onHeaderCollapseRequested(self) -> None:
        self.toggleCollapse()
        self.CollapseRequested.emit()

    def _onDockFlipRequested(self) -> None:
        self.toggleDockSide()

    def _onItemClicked(self, item: SideBarItem) -> None:
        self._xapplySelection(item)
        self.ItemClicked.emit(item)

    def _xallItems(self) -> List[SideBarItem]:
        lResult: List[SideBarItem] = list(self._rootItems)
        for lGroup in self._groups:
            lResult.extend(lGroup.CollectItems())
        return lResult

    def _xapplySelection(self, item: SideBarItem) -> None:
        for lItem in self._xallItems():
            lItem.active = False
            lItem.Selected = False

        item.active = True
        self._activeItem = item

        for lGroup in self._groups:
            lChain = lGroup.FindAncestorHeaders(item)
            for lHeader in lChain:
                if lHeader is not item:
                    lHeader.Selected = True