# ==================================================================================
# src/jAGQt/widgets/SideBar/components/__sideBarGroup.py
# ==================================================================================
from typing import Callable, Optional, Union

# ==================================================================================
from PySide6.QtCore import QEasingCurve, Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QBoxLayout, QSizePolicy, QStyle, QWidget

# ==================================================================================
from jAGQt.types.components import ComponentBase
from jAGQt.utilities import AnimateProperty, newLayout

# ==================================================================================
from .__sideBarIcon import SideBarIcon
from .__sideBarItem import IconPosition, ItemDisplayMode, SideBarItem
from .__sideBarSeparator import SeparatorType, SideBarSeparator


# ==================================================================================
class SideBarGroupHeader(SideBarItem):
    """Group header built on SideBarItem (selection / hover / QSS as one unit).

    Header-only features layered on the base item:
      1. Distinct objectName for QSS hierarchy
      2. Expand/collapse indicator (trailing icon)
      3. Title label objectName for section typography
      4. Indicator visibility when the whole sidebar is collapsed
    """

    def __init__(
        self, title: str = "", icon: Optional[Union[QIcon, QPixmap, str]] = None,
        iconSize: int = 20, parent: Optional[QWidget] = None, *args, **kwargs,
    ) -> None:
        super().__init__(
            text=title, icon=icon, displayMode=ItemDisplayMode.IconAndText,
            iconPosition=IconPosition.Left, iconSize=iconSize, spacing=6,
            parent=parent, *args, **kwargs,
        )

        # 1) Header identity for QSS (overrides SideBarItem objectName)
        self.setObjectName("SideBarGroupHeader")

        # 3) Section title typography hook
        self.TextWidget.setObjectName("SideBarGroupTitle")

        # 2) Expand/collapse indicator
        lIndicatorSize = max(12, min(iconSize - 4, 16))
        self._indicator = SideBarIcon(icon=None, iconSize=lIndicatorSize, parent=self)
        self._indicator.setObjectName("SideBarGroupIndicator")
        self._indicator.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._indicator.setAutoFillBackground(False)

        self._rebuildLayout()

    # ----- header features -----------------------------------------------------
    def SetExpanded(self, expanded: bool) -> None:
        """Update trailing indicator for expanded vs collapsed group body."""
        lStyle = self.style()
        if expanded:
            lIcon = lStyle.standardIcon(QStyle.StandardPixmap.SP_ArrowDown)
        else:
            lIcon = lStyle.standardIcon(QStyle.StandardPixmap.SP_ArrowRight)
        self._indicator.SetIcon(lIcon)

    def SetIndicatorVisible(self, visible: bool) -> None:
        self._indicator.setVisible(bool(visible))

    @property
    def Indicator(self) -> SideBarIcon:
        return self._indicator

    # ----- layout: base item + trailing indicator -----------------------------
    def _rebuildLayout(self) -> None:
        # Base icon + text arrangement from SideBarItem
        super()._rebuildLayout()

        # Drop the trailing stretch SideBarItem adds, then append indicator
        if self._layout.count() > 0:
            lLast = self._layout.itemAt(self._layout.count() - 1)
            if lLast is not None and lLast.spacerItem() is not None:
                self._layout.takeAt(self._layout.count() - 1)

        if hasattr(self, "_indicator"):
            self._layout.addWidget(self._indicator)


# ==================================================================================
class SideBarGroup(QWidget, ComponentBase):
    """Collapsible section composed of SideBarGroupHeader + body of SideBarItems.

    Selection / hover styling is entirely owned by the header (a SideBarItem).
    """

    Toggled = Signal(bool)
    ItemClicked = Signal(object)

    def __init__(
        self, title: str = "", icon: Optional[Union[QIcon, QPixmap, str]] = None,
        iconSize: int = 20, startCollapsed: bool = False, animationDurationMs: int = 180,
        spacing: int = 2, parent: Optional[QWidget] = None, *args, **kwargs,
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

        # Header = SideBarItem + header features
        self._header = SideBarGroupHeader(
            title=title,
            icon=icon,
            iconSize=self._iconSize,
            parent=self,
        )
        self._header.Clicked.connect(self._onHeaderClicked)

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

    # ==================================================================================
    def AddItem(
        self, text: str = "", icon: Optional[Union[QIcon, QPixmap, str]] = None,
        displayMode: ItemDisplayMode = ItemDisplayMode.IconAndText,
        iconPosition: IconPosition = IconPosition.Left, iconSize: Optional[int] = None,
        callback: Optional[Callable] = None,
    ) -> SideBarItem:
        lSize = iconSize if iconSize is not None else self._iconSize
        lItem = SideBarItem(
            text=text, icon=icon, displayMode=displayMode, iconPosition=iconPosition,
            iconSize=lSize, callback=callback, parent=self._body,
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

        self._header.TextWidget.setVisible(not self._sidebarCollapsed)
        self._header.SetIndicatorVisible(not self._sidebarCollapsed)
        if self._sidebarCollapsed:
            self._header.DisplayMode = ItemDisplayMode.IconOnly
        else:
            self._header.DisplayMode = ItemDisplayMode.IconAndText

        for lIdx in range(self._bodyLayout.count()):
            lW = self._bodyLayout.itemAt(lIdx)
            if lW and isinstance(lW.widget(), SideBarItem):
                lW.widget().DisplayMode = lMode

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
    def Selected(self) -> bool:
        return self._selected

    @Selected.setter
    def Selected(self, value: bool) -> None:
        lValue = bool(value)
        if lValue == self._selected:
            return
        self._selected = lValue
        # Selection highlight is owned by the base item machinery
        self._header.Selected = lValue

    @property
    def Title(self) -> str:
        return self._header.Text

    @Title.setter
    def Title(self, value: str) -> None:
        self._header.Text = value

    @property
    def IconSize(self) -> int:
        return self._iconSize

    @IconSize.setter
    def IconSize(self, value: int) -> None:
        lSize = max(1, int(value))
        if lSize == self._iconSize: return
        self._iconSize = lSize
        self._header.IconSize = lSize

    @property
    def AnimationDurationMs(self) -> int:
        return self._animationDurationMs

    @AnimationDurationMs.setter
    def AnimationDurationMs(self, value: int) -> None:
        self._animationDurationMs = max(0, int(value))

    @property
    def HeaderWidget(self) -> SideBarGroupHeader:
        return self._header

    @property
    def BodyWidget(self) -> QWidget:
        return self._body

    def _onHeaderClicked(self, _item: SideBarItem) -> None:
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

    def _applyFinalBodyHeight(self) -> None:
        if self._collapsed:
            self._body.setMaximumHeight(0)
            self._body.setVisible(False)
        else:
            self._body.setVisible(True)
            self._body.setMaximumHeight(16777215)

    def _applyCollapsedState(self, animate: bool = True) -> None:
        self._header.SetExpanded(not self._collapsed)

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
            self._body, "maximumHeight", lStart, lTargetHeight,
            durationMs=self._animationDurationMs, easing=QEasingCurve.Type.OutCubic,
            onFinished=self._onAnimationFinished,
        )

    def _onAnimationFinished(self) -> None:
        self._activeAnimation = None
        self._applyFinalBodyHeight()
