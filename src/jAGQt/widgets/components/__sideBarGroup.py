# ==================================================================================
# src/jAGQt/widgets/components/__sideBarGroup.py
# ==================================================================================
from typing import Callable, Optional, Union

# ==================================================================================
from PySide6.QtCore import QEasingCurve, Qt, Signal
from PySide6.QtGui import QColor, QIcon, QMouseEvent, QPalette, QPixmap
from PySide6.QtWidgets import QBoxLayout, QSizePolicy, QStyle, QWidget

# ==================================================================================
from jAGQt.types.components import ComponentBase
from jAGQt.utilities import AnimateProperty, newLayout

# ==================================================================================
from .__sideBarIcon import SideBarIcon
from .__sideBarItem import IconPosition, ItemDisplayMode, SideBarItem
from .__sideBarSeparator import SeparatorType, SideBarSeparator
from .__sideBarText import SideBarText


# ==================================================================================
_C_HEADER_OBJECT_NAME = "SideBarGroupHeader"
_C_HEADER_SELECTED_OBJECT_NAME = "SideBarGroupHeaderSelected"

_C_SELECTED_BG = QColor("#1c2832")
_C_IDLE_BG = QColor("#22262c")


# ==================================================================================
class SideBarGroup(QWidget, ComponentBase):
    """Independent collapsible section/group for the SideBar."""

    Toggled = Signal(bool)
    ItemClicked = Signal(object)

    def __init__(
        self,
        title: str = "",
        icon: Optional[Union[QIcon, QPixmap, str]] = None,
        iconSize: int = 20,
        startCollapsed: bool = False,
        animationDurationMs: int = 180,
        spacing: int = 2,
        parent: Optional[QWidget] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)

        self.setObjectName("SideBarGroup")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._collapsed: bool = startCollapsed
        self._selected: bool = False
        self._iconSize: int = max(1, iconSize)
        self._animationDurationMs: int = max(0, animationDurationMs)
        self._activeAnimation = None
        self._cachedSelectedItem: Optional[SideBarItem] = None
        self._sidebarCollapsed: bool = False

        # ----- Header --------------------------------------------------------
        self._header = QWidget(self)
        self._header.setObjectName(_C_HEADER_OBJECT_NAME)
        self._header.setCursor(Qt.CursorShape.PointingHandCursor)
        self._header.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._header.setAutoFillBackground(True)
        self._header.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self._iconWidget = SideBarIcon(icon=icon, iconSize=self._iconSize, parent=self._header)
        self._titleWidget = SideBarText(text=title, parent=self._header)
        self._titleWidget.setObjectName("SideBarGroupTitle")

        lIndicatorSize = max(12, min(self._iconSize - 4, 16))
        self._indicator = SideBarIcon(icon=None, iconSize=lIndicatorSize, parent=self._header)
        self._indicator.setObjectName("SideBarGroupIndicator")

        lHeaderLayout: QBoxLayout = newLayout(
            QBoxLayout, spacing=6, margins=(8, 6, 8, 6)
        )
        lHeaderLayout.setDirection(QBoxLayout.Direction.LeftToRight)
        self._header.setLayout(lHeaderLayout)
        lHeaderLayout.addWidget(self._iconWidget)
        lHeaderLayout.addWidget(self._titleWidget, 1)
        lHeaderLayout.addWidget(self._indicator)

        self._header.mousePressEvent = self._onHeaderClicked  # type: ignore

        # ----- Body ----------------------------------------------------------
        self._body = QWidget(self)
        self._body.setObjectName("SideBarGroupBody")
        self._body.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        self._bodyLayout: QBoxLayout = newLayout(
            QBoxLayout, spacing=spacing, margins=(4, 0, 4, 4)
        )
        self._bodyLayout.setDirection(QBoxLayout.Direction.TopToBottom)
        self._bodyLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._body.setLayout(self._bodyLayout)

        self._layout: QBoxLayout = newLayout(QBoxLayout, spacing=0, margins=(0, 0, 0, 0))
        self._layout.setDirection(QBoxLayout.Direction.TopToBottom)
        self.setLayout(self._layout)
        self._layout.addWidget(self._header)
        self._layout.addWidget(self._body)

        self._applyCollapsedState(animate=False)
        self._applySelectedState()

    # ================================================================================== public API – children
    def AddItem(
        self,
        text: str = "",
        icon: Optional[Union[QIcon, QPixmap, str]] = None,
        displayMode: ItemDisplayMode = ItemDisplayMode.IconAndText,
        iconPosition: IconPosition = IconPosition.Left,
        iconSize: Optional[int] = None,
        callback: Optional[Callable] = None,
    ) -> SideBarItem:
        lSize = iconSize if iconSize is not None else self._iconSize
        lItem = SideBarItem(
            text=text,
            icon=icon,
            displayMode=displayMode,
            iconPosition=iconPosition,
            iconSize=lSize,
            callback=callback,
            parent=self._body,
        )
        lItem.Clicked.connect(self._onChildItemClicked)
        self._bodyLayout.addWidget(lItem)
        if self._sidebarCollapsed:
            lItem.DisplayMode = ItemDisplayMode.IconOnly
        return lItem

    def AddSeparator(self, separatorType: SeparatorType = SeparatorType.Line) -> SideBarSeparator:
        lSep = SideBarSeparator(separatorType=separatorType, parent=self._body)
        self._bodyLayout.addWidget(lSep)
        return lSep

    def AddStretch(self, stretch: int = 1) -> None:
        self._bodyLayout.addStretch(stretch)

    def Clear(self) -> None:
        self._cachedSelectedItem = None
        while self._bodyLayout.count():
            lItem = self._bodyLayout.takeAt(0)
            if lItem.widget():
                lItem.widget().setParent(None)
                lItem.widget().deleteLater()

    def ContainsItem(self, item: SideBarItem) -> bool:
        for lIdx in range(self._bodyLayout.count()):
            lW = self._bodyLayout.itemAt(lIdx)
            if lW and lW.widget() is item:
                return True
        return False

    def GetDefaultItem(self) -> Optional[SideBarItem]:
        for lIdx in range(self._bodyLayout.count()):
            lW = self._bodyLayout.itemAt(lIdx)
            if lW and isinstance(lW.widget(), SideBarItem):
                return lW.widget()
        return None

    def GetSelectionTarget(self) -> Optional[SideBarItem]:
        if self._cachedSelectedItem is not None and self.ContainsItem(self._cachedSelectedItem):
            return self._cachedSelectedItem
        return self.GetDefaultItem()

    def SetSidebarCollapsed(self, collapsed: bool) -> None:
        self._sidebarCollapsed = bool(collapsed)
        lMode = ItemDisplayMode.IconOnly if self._sidebarCollapsed else ItemDisplayMode.IconAndText

        self._titleWidget.setVisible(not self._sidebarCollapsed)
        self._indicator.setVisible(not self._sidebarCollapsed)

        for lIdx in range(self._bodyLayout.count()):
            lW = self._bodyLayout.itemAt(lIdx)
            if lW and isinstance(lW.widget(), SideBarItem):
                lW.widget().DisplayMode = lMode

        if self._sidebarCollapsed:
            self.Collapse(animate=False)

    # ================================================================================== public API – collapse
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
    def Selected(self) -> bool:
        return self._selected

    @Selected.setter
    def Selected(self, value: bool) -> None:
        lValue = bool(value)
        if lValue == self._selected:
            return
        self._selected = lValue
        self._applySelectedState()

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
        lSize = max(1, int(value))
        if lSize == self._iconSize:
            return
        self._iconSize = lSize
        self._iconWidget.IconSize = lSize

    @property
    def AnimationDurationMs(self) -> int:
        return self._animationDurationMs

    @AnimationDurationMs.setter
    def AnimationDurationMs(self, value: int) -> None:
        self._animationDurationMs = max(0, int(value))

    @property
    def HeaderWidget(self) -> QWidget:
        return self._header

    @property
    def BodyWidget(self) -> QWidget:
        return self._body

    # ================================================================================== private
    def _standardIcon(self, standardPixmap: QStyle.StandardPixmap) -> QIcon:
        return self.style().standardIcon(standardPixmap)

    def _refreshIndicatorIcon(self) -> None:
        if self._collapsed:
            lIcon = self._standardIcon(QStyle.StandardPixmap.SP_ArrowRight)
        else:
            lIcon = self._standardIcon(QStyle.StandardPixmap.SP_ArrowDown)
        self._indicator.SetIcon(lIcon)

    def _onHeaderClicked(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return
        if self._sidebarCollapsed:
            return

        self.Expand(animate=True)

        lTarget = self.GetSelectionTarget()
        if lTarget is not None:
            self._cachedSelectedItem = lTarget
            self.ItemClicked.emit(lTarget)
        else:
            self.Selected = True

    def _onChildItemClicked(self, item: SideBarItem) -> None:
        self._cachedSelectedItem = item
        self.ItemClicked.emit(item)

    def _applySelectedState(self) -> None:
        self._header.setObjectName(
            _C_HEADER_SELECTED_OBJECT_NAME if self._selected else _C_HEADER_OBJECT_NAME
        )

        lPalette = self._header.palette()
        lBg = _C_SELECTED_BG if self._selected else _C_IDLE_BG
        lPalette.setColor(QPalette.ColorRole.Window, lBg)
        lPalette.setColor(QPalette.ColorRole.Base, lBg)
        lPalette.setColor(QPalette.ColorRole.Button, lBg)
        self._header.setPalette(lPalette)
        self._header.setAutoFillBackground(True)

        self._header.style().unpolish(self._header)
        self._header.style().polish(self._header)
        self._header.update()

    def _applyFinalBodyHeight(self) -> None:
        if self._collapsed:
            self._body.setMaximumHeight(0)
            self._body.setVisible(False)
        else:
            self._body.setVisible(True)
            self._body.setMaximumHeight(16777215)

    def _applyCollapsedState(self, animate: bool = True) -> None:
        self._refreshIndicatorIcon()

        if self._collapsed:
            lTargetHeight = 0
            lStart = self._body.height() if self._body.isVisible() else 0
        else:
            self._body.setVisible(True)
            self._body.setMaximumHeight(16777215)
            lTargetHeight = max(0, self._body.sizeHint().height())
            lStart = 0 if not self._body.isVisible() else self._body.height()
            if lStart <= 0:
                lStart = 0

        if not animate or self._animationDurationMs <= 0 or lStart == lTargetHeight:
            self._applyFinalBodyHeight()
            return

        self._body.setVisible(True)
        self._body.setMaximumHeight(max(lStart, lTargetHeight, 1))

        self._activeAnimation = AnimateProperty(
            self._body,
            "maximumHeight",
            lStart,
            lTargetHeight,
            durationMs=self._animationDurationMs,
            easing=QEasingCurve.Type.OutCubic,
            onFinished=self._onAnimationFinished,
        )

    def _onAnimationFinished(self) -> None:
        self._activeAnimation = None
        self._applyFinalBodyHeight()
