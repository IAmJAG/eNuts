# ==================================================================================
# src/jAGQt/widgets/components/__sideBarItem.py
# ==================================================================================
from enum import Enum, auto
from typing import Callable, Optional, Union

# ==================================================================================
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QMouseEvent, QPixmap
from PySide6.QtWidgets import QBoxLayout, QSizePolicy, QWidget

# ==================================================================================
from jAGQt.types.components import ComponentBase
from jAGQt.utilities import newLayout

# ==================================================================================
from .__sideBarIcon import SideBarIcon
from .__sideBarText import SideBarText


# ==================================================================================
class ItemDisplayMode(Enum):
    IconOnly = auto()
    TextOnly = auto()
    IconAndText = auto()


class IconPosition(Enum):
    Left = auto()
    Right = auto()
    Top = auto()
    Bottom = auto()


# ==================================================================================
class SideBarItem(QWidget, ComponentBase):
    """Independent SideBar item that composes Icon + Text.

    Supports IconOnly / TextOnly / IconAndText modes and flexible alignment.
    """

    Clicked = Signal(object)  # emits self

    def __init__(
        self, text: str = "", icon: Optional[Union[QIcon, QPixmap, str]] = None,
        displayMode: ItemDisplayMode = ItemDisplayMode.IconAndText,
        iconPosition: IconPosition = IconPosition.Left, iconSize: int = 24,
        spacing: int = 8, callback: Optional[Callable] = None, parent: Optional[QWidget] = None,
        *args, **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)

        self.setObjectName("SideBarItem")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._displayMode: ItemDisplayMode = displayMode
        self._iconPosition: IconPosition = iconPosition
        self._callback: Optional[Callable] = callback
        self._selected: bool = False

        self._iconWidget = SideBarIcon(icon=icon, iconSize=iconSize, parent=self)
        self._textWidget = SideBarText(text=text, parent=self)

        self._layout: QBoxLayout = newLayout(QBoxLayout, spacing=spacing, margins=(6, 4, 6, 4))
        self.setLayout(self._layout)

        self._rebuildLayout()

    # ================================================================================== public API
    def SetText(self, text: str) -> None:
        self._textWidget.Text = text

    def SetIcon(self, icon: Optional[Union[QIcon, QPixmap, str]]) -> None:
        self._iconWidget.SetIcon(icon)

    def SetCallback(self, callback: Optional[Callable]) -> None:
        self._callback = callback

    def SetSelected(self, selected: bool) -> None:
        self.Selected = selected

    # ================================================================================== properties
    @property
    def Text(self) -> str:
        return self._textWidget.Text

    @Text.setter
    def Text(self, value: str) -> None:
        self._textWidget.Text = value

    @property
    def IconSize(self) -> int:
        return self._iconWidget.IconSize

    @IconSize.setter
    def IconSize(self, value: int) -> None:
        self._iconWidget.IconSize = value

    @property
    def DisplayMode(self) -> ItemDisplayMode:
        return self._displayMode

    @DisplayMode.setter
    def DisplayMode(self, value: ItemDisplayMode) -> None:
        if value == self._displayMode: return
        self._displayMode = value
        self._rebuildLayout()

    @property
    def IconPosition(self) -> IconPosition:
        return self._iconPosition

    @IconPosition.setter
    def IconPosition(self, value: IconPosition) -> None:
        if value == self._iconPosition:
            return
        self._iconPosition = value
        self._rebuildLayout()

    @property
    def Selected(self) -> bool:
        return self._selected

    @Selected.setter
    def Selected(self, value: bool) -> None:
        if value == self._selected:
            return
        self._selected = bool(value)
        self.setProperty("selected", "true" if self._selected else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    @property
    def IconWidget(self) -> SideBarIcon:
        return self._iconWidget

    @property
    def TextWidget(self) -> SideBarText:
        return self._textWidget

    # ================================================================================== events
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.Clicked.emit(self)
            if self._callback is not None:
                self._callback(self)
        super().mousePressEvent(event)

    def enterEvent(self, event) -> None:
        self.setProperty("hover", "true")
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self.setProperty("hover", "false")
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
        super().leaveEvent(event)

    # ================================================================================== private
    def _rebuildLayout(self) -> None:
        # Only detach from layout — keep parent=self so widgets never become
        # transient top-level windows (which flash as mini-windows on screen).
        while self._layout.count(): self._layout.takeAt(0)

        lShowIcon = self._displayMode in (ItemDisplayMode.IconOnly, ItemDisplayMode.IconAndText)
        lShowText = self._displayMode in (ItemDisplayMode.TextOnly, ItemDisplayMode.IconAndText)

        self._iconWidget.setVisible(lShowIcon)
        self._textWidget.setVisible(lShowText)

        if self._iconPosition in (IconPosition.Left, IconPosition.Right):
            self._layout.setDirection(QBoxLayout.Direction.LeftToRight)
            
        else:
            self._layout.setDirection(QBoxLayout.Direction.TopToBottom)

        if self._iconPosition in (IconPosition.Left, IconPosition.Top):
            if lShowIcon:
                self._layout.addWidget(self._iconWidget)

            if lShowText:
                self._layout.addWidget(self._textWidget, 1)

        else:
            if lShowText:
                self._layout.addWidget(self._textWidget, 1)

            if lShowIcon:
                self._layout.addWidget(self._iconWidget)

        self._layout.addStretch(0)
