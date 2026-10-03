# ==================================================================================
# src/jAGQt/widgets/components/__sideBarGroup.py
# ==================================================================================
from typing import Callable, Optional, Union

# ==================================================================================
from PySide6.QtCore import QEasingCurve, Qt, Signal
from PySide6.QtGui import QIcon, QMouseEvent, QPixmap
from PySide6.QtWidgets import QBoxLayout, QSizePolicy, QWidget

# ==================================================================================
from jAGQt.types.components import ComponentBase
from jAGQt.utilities import AnimateProperty, newLayout

# ==================================================================================
from .__sideBarIcon import SideBarIcon
from .__sideBarItem import IconPosition, ItemDisplayMode, SideBarItem
from .__sideBarSeparator import SeparatorType, SideBarSeparator
from .__sideBarText import SideBarText


# ==================================================================================
class SideBarGroup(QWidget, ComponentBase):
    """Independent collapsible section/group for the SideBar.

    Contains a clickable header and a body that can hold items, separators,
    and nested groups. Collapse/expand animates the body height.
    """

    Toggled = Signal(bool)          # emits new collapsed state
    ItemClicked = Signal(object)    # re-emits child SideBarItem clicks

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
        self._iconSize: int = max(1, iconSize)
        self._animationDurationMs: int = max(0, animationDurationMs)
        self._activeAnimation = None

        # ----- Header (clickable) --------------------------------------------
        self._header = QWidget(self)
        self._header.setObjectName("SideBarGroupHeader")
        self._header.setCursor(Qt.CursorShape.PointingHandCursor)
        self._header.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._header.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self._iconWidget = SideBarIcon(icon=icon, iconSize=self._iconSize, parent=self._header)
        self._titleWidget = SideBarText(text=title, parent=self._header)
        self._titleWidget.setObjectName("SideBarGroupTitle")

        self._indicator = SideBarText(text="▾", parent=self._header)
        self._indicator.setObjectName("SideBarGroupIndicator")
        self._indicator.setFixedWidth(20)
        self._indicator.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)

        lHeaderLayout: QBoxLayout = newLayout(
            QBoxLayout, spacing=6, margins=(8, 6, 8, 6)
        )
        lHeaderLayout.setDirection(QBoxLayout.Direction.LeftToRight)
        self._header.setLayout(lHeaderLayout)
        lHeaderLayout.addWidget(self._iconWidget)
        lHeaderLayout.addWidget(self._titleWidget, 1)
        lHeaderLayout.addWidget(self._indicator)

        self._header.mousePressEvent = self._onHeaderClicked  # type: ignore

        # ----- Body (holds children) -----------------------------------------
        self._body = QWidget(self)
        self._body.setObjectName("SideBarGroupBody")
        self._body.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        self._bodyLayout: QBoxLayout = newLayout(
            QBoxLayout, spacing=spacing, margins=(4, 0, 4, 4)
        )
        self._bodyLayout.setDirection(QBoxLayout.Direction.TopToBottom)
        self._bodyLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._body.setLayout(self._bodyLayout)

        # ----- Root layout ---------------------------------------------------
        self._layout: QBoxLayout = newLayout(QBoxLayout, spacing=0, margins=(0, 0, 0, 0))
        self._layout.setDirection(QBoxLayout.Direction.TopToBottom)
        self.setLayout(self._layout)
        self._layout.addWidget(self._header)
        self._layout.addWidget(self._body)

        self._applyCollapsedState(animate=False)

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
        return lItem

    def AddSeparator(self, separatorType: SeparatorType = SeparatorType.Line) -> SideBarSeparator:
        lSep = SideBarSeparator(separatorType=separatorType, parent=self._body)
        self._bodyLayout.addWidget(lSep)
        return lSep

    def AddStretch(self, stretch: int = 1) -> None:
        self._bodyLayout.addStretch(stretch)

    def Clear(self) -> None:
        while self._bodyLayout.count():
            lItem = self._bodyLayout.takeAt(0)
            if lItem.widget():
                lItem.widget().setParent(None)
                lItem.widget().deleteLater()

    # ================================================================================== public API – collapse
    def Collapse(self, animate: bool = True) -> None:
        if self._collapsed:
            return
        self._collapsed = True
        self._applyCollapsedState(animate=animate)
        self.Toggled.emit(True)

    def Expand(self, animate: bool = True) -> None:
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
    def _onHeaderClicked(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.Toggle()

    def _onChildItemClicked(self, item: SideBarItem) -> None:
        self.ItemClicked.emit(item)

    def _applyCollapsedState(self, animate: bool = True) -> None:
        self._indicator.Text = "▸" if self._collapsed else "▾"
        self._header.setProperty("collapsed", self._collapsed)
        self._header.style().unpolish(self._header)
        self._header.style().polish(self._header)

        if self._collapsed:
            lTargetHeight = 0
        else:
            # Ensure body is visible so sizeHint is accurate
            self._body.setVisible(True)
            self._body.setMaximumHeight(16777215)
            lTargetHeight = self._body.sizeHint().height()

        if animate and self._animationDurationMs > 0:
            lStart = self._body.height() if self._body.isVisible() else 0
            if lStart == lTargetHeight and self._collapsed:
                self._body.setVisible(False)
                self._body.setMaximumHeight(0)
                return

            self._body.setVisible(True)
            self._body.setMaximumHeight(16777215)

            self._activeAnimation = AnimateProperty(
                self._body,
                "maximumHeight",
                lStart if lStart > 0 else self._body.sizeHint().height(),
                lTargetHeight,
                durationMs=self._animationDurationMs,
                easing=QEasingCurve.Type.OutCubic,
                onFinished=self._onAnimationFinished,
            )
        else:
            if self._collapsed:
                self._body.setMaximumHeight(0)
                self._body.setVisible(False)
            else:
                self._body.setVisible(True)
                self._body.setMaximumHeight(16777215)

    def _onAnimationFinished(self) -> None:
        self._activeAnimation = None
        if self._collapsed:
            self._body.setVisible(False)
            self._body.setMaximumHeight(0)
        else:
            self._body.setMaximumHeight(16777215)
