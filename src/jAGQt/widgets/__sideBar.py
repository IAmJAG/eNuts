# ==================================================================================
# src/jAGQt/widgets/__sideBar.py
# ==================================================================================
from enum import Enum, auto
from typing import Callable, Optional, Union

# ==================================================================================
from PySide6.QtCore import QEasingCurve, Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QBoxLayout, QLayoutItem, QSizePolicy, QWidget

# ==================================================================================
from jAGQt.types.components import ComponentBase
from jAGQt.utilities import AnimateProperty, newLayout

# ==================================================================================
from .components import (
    IconPosition,
    ItemDisplayMode,
    SeparatorType,
    SideBarContent,
    SideBarGroup,
    SideBarHeader,
    SideBarItem,
    SideBarSeparator,
)


# ==================================================================================
class DockPosition(Enum):
    Left = auto()
    Right = auto()


# ==================================================================================
class SideBar(QWidget, ComponentBase):
    """Main SideBar composer.

    Independent components are composed here. All key behaviours are configurable.
    Menu morph methods (addWidget / insertWidget / …) operate on the content layout.
    """

    ItemClicked = Signal(object)
    CollapsedChanged = Signal(bool)
    WidthChanged = Signal(int)

    def __init__(
        self,
        title: str = "",
        icon: Optional[Union[QIcon, QPixmap, str]] = None,
        expandedWidth: int = 240,
        collapsedWidth: int = 48,
        iconSize: int = 24,
        dockPosition: DockPosition = DockPosition.Left,
        startCollapsed: bool = False,
        autoCollapse: bool = False,
        animationDurationMs: int = 220,
        parent: Optional[QWidget] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)

        self.setObjectName("SideBar")
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._expandedWidth: int = max(collapsedWidth, expandedWidth)
        self._collapsedWidth: int = max(1, collapsedWidth)
        self._iconSize: int = max(1, iconSize)
        self._dockPosition: DockPosition = dockPosition
        self._autoCollapse: bool = autoCollapse
        self._collapsed: bool = startCollapsed
        self._animationDurationMs: int = max(0, animationDurationMs)
        self._activeAnimation = None

        self._header = SideBarHeader(
            title=title,
            icon=icon,
            iconSize=self._iconSize,
            showCollapseButton=True,
            parent=self,
        )
        self._content = SideBarContent(parent=self)

        self._layout: QBoxLayout = newLayout(
            QBoxLayout, spacing=0, margins=(0, 0, 1, 0)
        )
        self._layout.setDirection(QBoxLayout.Direction.TopToBottom)
        self.setLayout(self._layout)

        self._layout.addWidget(self._header)
        self._layout.addWidget(self._content, 1)

        self._header.CollapseRequested.connect(self.ToggleCollapsed)

        self._applyCollapsedState(animate=False)

    # ================================================================================== public API – items / groups
    def AddItem(
        self, text: str = "", icon: Optional[Union[QIcon, QPixmap, str]] = None,
        displayMode: ItemDisplayMode = ItemDisplayMode.IconAndText,
        iconPosition: IconPosition = IconPosition.Left, callback: Optional[Callable] = None,
    ) -> SideBarItem:
        lItem = SideBarItem(
            text=text, icon=icon, displayMode=displayMode, iconPosition=iconPosition,
            iconSize=self._iconSize, callback=callback, parent=self._content.Container,
        )
        lItem.Clicked.connect(self._onItemClicked)
        self._content.AddWidget(lItem)
        self._syncItemDisplayMode(lItem)
        return lItem

    def AddGroup(
        self, title: str = "", icon: Optional[Union[QIcon, QPixmap, str]] = None,
        startCollapsed: bool = False, iconSize: Optional[int] = None,
    ) -> SideBarGroup:
        lSize = iconSize if iconSize is not None else max(1, self._iconSize - 2)
        lGroup = SideBarGroup(
            title=title,
            icon=icon,
            iconSize=lSize,
            startCollapsed=startCollapsed,
            animationDurationMs=self._animationDurationMs,
            parent=self._content.Container,
        )
        lGroup.ItemClicked.connect(self._onItemClicked)
        self._content.AddWidget(lGroup)
        if self._collapsed:
            lGroup.SetSidebarCollapsed(True)
        return lGroup

    def AddSeparator(self, separatorType: SeparatorType = SeparatorType.Line) -> SideBarSeparator:
        lSep = SideBarSeparator(separatorType=separatorType, parent=self._content.Container)
        self._content.AddWidget(lSep)
        return lSep

    def AddStretch(self, stretch: int = 1) -> None:
        self._content.AddStretch(stretch)

    def ClearItems(self) -> None:
        self._content.Clear()

    # ================================================================================== menu morph methods (content layout)
    def addWidget(self, widget: QWidget, stretch: int = 0, alignment: Qt.AlignmentFlag = Qt.AlignmentFlag(0)) -> None:
        self._content.ContentLayout.addWidget(widget, stretch, alignment)

    def insertWidget(self, index: int, widget: QWidget, stretch: int = 0, alignment: Qt.AlignmentFlag = Qt.AlignmentFlag(0)) -> None:
        self._content.ContentLayout.insertWidget(index, widget, stretch, alignment)

    def addLayout(self, layout, stretch: int = 0) -> None:
        self._content.ContentLayout.addLayout(layout, stretch)

    def insertLayout(self, index: int, layout, stretch: int = 0) -> None:
        self._content.ContentLayout.insertLayout(index, layout, stretch)

    def addItem(self, item: QLayoutItem) -> None:
        self._content.ContentLayout.addItem(item)

    def insertItem(self, index: int, item: QLayoutItem) -> None:
        self._content.ContentLayout.insertItem(index, item)

    def addStretch(self, stretch: int = 0) -> None:
        self._content.ContentLayout.addStretch(stretch)

    def addSpacing(self, size: int) -> None:
        self._content.ContentLayout.addSpacing(size)

    def addStrut(self, size: int) -> None:
        self._content.ContentLayout.addStrut(size)

    def removeWidget(self, widget: QWidget) -> None:
        self._content.ContentLayout.removeWidget(widget)

    def removeItem(self, item: QLayoutItem) -> None:
        self._content.ContentLayout.removeItem(item)

    def takeAt(self, index: int) -> QLayoutItem:
        return self._content.ContentLayout.takeAt(index)

    # ================================================================================== public API – collapse
    def Collapse(self, animate: bool = True) -> None:
        if self._collapsed:
            return
        self._collapsed = True
        self._applyCollapsedState(animate=animate)
        self.CollapsedChanged.emit(True)

    def Expand(self, animate: bool = True) -> None:
        if not self._collapsed:
            return
        self._collapsed = False
        self._applyCollapsedState(animate=animate)
        self.CollapsedChanged.emit(False)

    def ToggleCollapsed(self, animate: bool = True) -> None:
        if self._collapsed:
            self.Expand(animate=animate)
        else:
            self.Collapse(animate=animate)

    # ================================================================================== properties
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
    def ExpandedWidth(self) -> int:
        return self._expandedWidth

    @ExpandedWidth.setter
    def ExpandedWidth(self, value: int) -> None:
        self._expandedWidth = max(self._collapsedWidth, int(value))
        if not self._collapsed:
            self._applyCollapsedState(animate=False)

    @property
    def CollapsedWidth(self) -> int:
        return self._collapsedWidth

    @CollapsedWidth.setter
    def CollapsedWidth(self, value: int) -> None:
        self._collapsedWidth = max(1, int(value))
        if self._collapsed:
            self._applyCollapsedState(animate=False)

    @property
    def IconSize(self) -> int:
        return self._iconSize

    @IconSize.setter
    def IconSize(self, value: int) -> None:
        lSize = max(1, int(value))
        if lSize == self._iconSize:
            return
        self._iconSize = lSize
        self._header.IconWidget.IconSize = lSize
        for lIdx in range(self._content.Count()):
            lW = self._content.ContentLayout.itemAt(lIdx)
            if lW is None:
                continue
            lWidget = lW.widget()
            if isinstance(lWidget, SideBarItem):
                lWidget.IconSize = lSize
            elif isinstance(lWidget, SideBarGroup):
                lWidget.IconSize = max(1, lSize - 2)

    @property
    def DockPosition(self) -> DockPosition:
        return self._dockPosition

    @DockPosition.setter
    def DockPosition(self, value: DockPosition) -> None:
        self._dockPosition = value

    @property
    def AutoCollapse(self) -> bool:
        return self._autoCollapse

    @AutoCollapse.setter
    def AutoCollapse(self, value: bool) -> None:
        self._autoCollapse = bool(value)

    @property
    def AnimationDurationMs(self) -> int:
        return self._animationDurationMs

    @AnimationDurationMs.setter
    def AnimationDurationMs(self, value: int) -> None:
        self._animationDurationMs = max(0, int(value))

    @property
    def Header(self) -> SideBarHeader:
        return self._header

    @property
    def Content(self) -> SideBarContent:
        return self._content

    # ================================================================================== private
    def _syncAllDisplayModes(self) -> None:
        lMode = ItemDisplayMode.IconOnly if self._collapsed else ItemDisplayMode.IconAndText

        self._header.TitleWidget.setVisible(not self._collapsed)
        self._header.SetCollapsed(self._collapsed)

        for lIdx in range(self._content.Count()):
            lW = self._content.ContentLayout.itemAt(lIdx)
            if lW is None: continue

            lWidget = lW.widget()
            if isinstance(lWidget, SideBarItem):
                lWidget.DisplayMode = lMode

            elif isinstance(lWidget, SideBarGroup):
                lWidget.SetSidebarCollapsed(self._collapsed)

    def _applyCollapsedState(self, animate: bool = True) -> None:
        lTargetWidth = self._collapsedWidth if self._collapsed else self._expandedWidth

        self._syncAllDisplayModes()

        if animate and self._animationDurationMs > 0 and self.width() != lTargetWidth:
            self.setMaximumWidth(16777215)
            self._activeAnimation = AnimateProperty(
                self, "minimumWidth", self.width(), lTargetWidth,
                durationMs=self._animationDurationMs, easing=QEasingCurve.Type.OutCubic,
                onFinished=self._onAnimationFinished,
            )
            AnimateProperty(
                self, "maximumWidth", self.width(), lTargetWidth,
                durationMs=self._animationDurationMs, easing=QEasingCurve.Type.OutCubic,
            )
            
        else:
            self.setFixedWidth(lTargetWidth)
            self._syncAllDisplayModes()
            self.WidthChanged.emit(lTargetWidth)

    def _onAnimationFinished(self) -> None:
        lWidth = self._collapsedWidth if self._collapsed else self._expandedWidth
        self.setFixedWidth(lWidth)
        self._activeAnimation = None
        self._syncAllDisplayModes()
        self.WidthChanged.emit(lWidth)

    def _onItemClicked(self, item: SideBarItem) -> None:
        for lIdx in range(self._content.Count()):
            lW = self._content.ContentLayout.itemAt(lIdx)
            if lW is None:
                continue
            lWidget = lW.widget()

            if isinstance(lWidget, SideBarItem):
                lWidget.Selected = (lWidget is item)

            elif isinstance(lWidget, SideBarGroup):
                lOwns = lWidget.ContainsItem(item)

                for lGIdx in range(lWidget.BodyWidget.layout().count()):
                    lGW = lWidget.BodyWidget.layout().itemAt(lGIdx)
                    if lGW and isinstance(lGW.widget(), SideBarItem):
                        lGW.widget().Selected = (lGW.widget() is item)

                lWidget.Selected = lOwns
                if lOwns:
                    lWidget.Expand(animate=True)
                else:
                    lWidget.Collapse(animate=True)

        self.ItemClicked.emit(item)

    def _syncItemDisplayMode(self, item: SideBarItem) -> None:
        if self._collapsed:
            item.DisplayMode = ItemDisplayMode.IconOnly

    def enterEvent(self, event) -> None:
        if self._autoCollapse and self._collapsed:
            self.Expand()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        if self._autoCollapse and not self._collapsed:
            self.Collapse()
        super().leaveEvent(event)
