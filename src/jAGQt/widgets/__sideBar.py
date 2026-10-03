# ==================================================================================
# src/jAGQt/widgets/__sideBar.py
# ==================================================================================
from enum import Enum, auto
from typing import Callable, Optional, Union

# ==================================================================================
from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QPropertyAnimation,
    Qt,
    Signal,
)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QBoxLayout, QSizePolicy, QWidget

# ==================================================================================
from jAGQt.types.components import ComponentBase
from jAGQt.utilities import newLayout

# ==================================================================================
from .components import (
    ItemDisplayMode,
    SideBarContent,
    SideBarHeader,
    SideBarIcon,
    SideBarItem,
    SideBarSeparator,
    SideBarText,
)
from .components.__sideBarItem import IconPosition
from .components.__sideBarSeparator import SeparatorType


# ==================================================================================
class DockPosition(Enum):
    Left = auto()
    Right = auto()


# ==================================================================================
class SideBar(QWidget, ComponentBase):
    """Main SideBar composer – Phase 1 foundation.

    Independent components are composed here. All key behaviours are configurable.
    """

    ItemClicked = Signal(object)          # emits SideBarItem
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

        # Configurable state
        self._expandedWidth: int = max(collapsedWidth, expandedWidth)
        self._collapsedWidth: int = max(1, collapsedWidth)
        self._iconSize: int = max(1, iconSize)
        self._dockPosition: DockPosition = dockPosition
        self._autoCollapse: bool = autoCollapse
        self._collapsed: bool = startCollapsed
        self._animationDurationMs: int = max(0, animationDurationMs)

        # Child components
        self._header = SideBarHeader(
            title=title,
            icon=icon,
            iconSize=self._iconSize,
            showCollapseButton=True,
            parent=self,
        )
        self._content = SideBarContent(parent=self)

        self._layout: QBoxLayout = newLayout(
            QBoxLayout, spacing=0, margins=(0, 0, 0, 0)
        )
        self._layout.setDirection(QBoxLayout.Direction.TopToBottom)
        self.setLayout(self._layout)

        self._layout.addWidget(self._header)
        self._layout.addWidget(self._content, 1)

        # Animation
        self._widthAnimation = QPropertyAnimation(self, b"minimumWidth", self)
        self._widthAnimation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._widthAnimation.setDuration(self._animationDurationMs)
        self._widthAnimation.finished.connect(self._onAnimationFinished)

        # Wire header collapse button
        self._header.CollapseRequested.connect(self.ToggleCollapsed)

        # Apply initial state
        self._applyCollapsedState(animate=False)

    # ================================================================================== public API – items
    def AddItem(
        self,
        text: str = "",
        icon: Optional[Union[QIcon, QPixmap, str]] = None,
        displayMode: ItemDisplayMode = ItemDisplayMode.IconAndText,
        iconPosition: IconPosition = IconPosition.Left,
        callback: Optional[Callable] = None,
    ) -> SideBarItem:
        lItem = SideBarItem(
            text=text,
            icon=icon,
            displayMode=displayMode,
            iconPosition=iconPosition,
            iconSize=self._iconSize,
            callback=callback,
            parent=self._content.Container,
        )
        lItem.Clicked.connect(self._onItemClicked)
        self._content.AddWidget(lItem)
        self._syncItemDisplayMode(lItem)
        return lItem

    def AddSeparator(self, separatorType: SeparatorType = SeparatorType.Line) -> SideBarSeparator:
        lSep = SideBarSeparator(separatorType=separatorType, parent=self._content.Container)
        self._content.AddWidget(lSep)
        return lSep

    def AddStretch(self, stretch: int = 1) -> None:
        self._content.AddStretch(stretch)

    def ClearItems(self) -> None:
        self._content.Clear()

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
        # Update existing items
        for lIdx in range(self._content.Count()):
            lItem = self._content.ContentLayout.itemAt(lIdx)
            if lItem and isinstance(lItem.widget(), SideBarItem):
                lItem.widget().IconSize = lSize

    @property
    def DockPosition(self) -> DockPosition:
        return self._dockPosition

    @DockPosition.setter
    def DockPosition(self, value: DockPosition) -> None:
        self._dockPosition = value
        # Future: layout mirroring / animation direction

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
        self._widthAnimation.setDuration(self._animationDurationMs)

    @property
    def Header(self) -> SideBarHeader:
        return self._header

    @property
    def Content(self) -> SideBarContent:
        return self._content

    # ================================================================================== private
    def _applyCollapsedState(self, animate: bool = True) -> None:
        lTargetWidth = self._collapsedWidth if self._collapsed else self._expandedWidth

        # Force icon-only when collapsed
        lMode = ItemDisplayMode.IconOnly if self._collapsed else ItemDisplayMode.IconAndText
        for lIdx in range(self._content.Count()):
            lItem = self._content.ContentLayout.itemAt(lIdx)
            if lItem and isinstance(lItem.widget(), SideBarItem):
                lItem.widget().DisplayMode = lMode

        self._header.TitleWidget.setVisible(not self._collapsed)

        if animate and self._animationDurationMs > 0:
            self._widthAnimation.stop()
            self._widthAnimation.setStartValue(self.width())
            self._widthAnimation.setEndValue(lTargetWidth)
            self._widthAnimation.start()
        else:
            self.setFixedWidth(lTargetWidth)
            self.WidthChanged.emit(lTargetWidth)

    def _onAnimationFinished(self) -> None:
        lWidth = self._collapsedWidth if self._collapsed else self._expandedWidth
        self.setFixedWidth(lWidth)
        self.WidthChanged.emit(lWidth)

    def _onItemClicked(self, item: SideBarItem) -> None:
        # Deselect others, select this one
        for lIdx in range(self._content.Count()):
            lW = self._content.ContentLayout.itemAt(lIdx)
            if lW and isinstance(lW.widget(), SideBarItem):
                lW.widget().Selected = (lW.widget() is item)
        self.ItemClicked.emit(item)

    def _syncItemDisplayMode(self, item: SideBarItem) -> None:
        if self._collapsed:
            item.DisplayMode = ItemDisplayMode.IconOnly

    # ================================================================================== auto-collapse helpers
    def enterEvent(self, event) -> None:
        if self._autoCollapse and self._collapsed:
            self.Expand()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        if self._autoCollapse and not self._collapsed:
            self.Collapse()
        super().leaveEvent(event)
