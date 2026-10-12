# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Callable, Optional, Union
from uuid import UUID, uuid4

# ==================================================================================
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QMouseEvent, QPixmap
from PySide6.QtWidgets import QBoxLayout, QSizePolicy, QWidget

# ==================================================================================
from ....utilities import newLayout
from ...components import ComponentBase
from ..types import SideBarIconPosition, SideBarItemDisplayMode, SideBarItemRole
from .__icon import Icon as SideBarIcon
from .__text import Text as SideBarText


# ==================================================================================
class Item(QWidget, ComponentBase):
    OBJECT_NAME = "W_SIDEBAR_ITEM"
    Clicked = Signal(object)

    def __init__(
        self, text: str = "", icon: Optional[Union[QIcon, QPixmap, str]] = None,
        displayMode: SideBarItemDisplayMode = SideBarItemDisplayMode.IconAndText,
        iconPosition: SideBarIconPosition = SideBarIconPosition.Left,
        iconSize: int = 24, depth: int = 0, role: SideBarItemRole = SideBarItemRole.Leaf,
        spacing: int = 8, callback: Optional[Callable] = None, id: Optional[str] = None,
        *args, **kwargs,
    ) -> None:
        OBJNAME: str = kwargs.pop("objectName", self.OBJECT_NAME)
        super().__init__(objectName=OBJNAME, *args, **kwargs)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._id: str = str(uuid4()) if id is None else str(id)
        self._displayMode: SideBarItemDisplayMode = displayMode
        self._iconPosition: SideBarIconPosition = iconPosition
        self._callback: Optional[Callable] = callback
        self._selected: bool = False
        self._active: bool = False
        self._depth: int = max(0, int(depth))
        self._role: SideBarItemRole = role

        self._text: str = text
        self._icon: Optional[Union[QIcon, QPixmap, str]] = icon
        self._iconSize: int = max(1, int(iconSize))
        self._spacing: int = max(0, int(spacing))

    def _wInitializeUI(self):
        text: str = self._text if self._text is not None else ""
        icon: Optional[Union[QIcon, QPixmap, str]] = self._icon
        iconSize: int = max(1, self._iconSize)
        spacing: int = max(0, self._spacing)

        del self._text
        del self._icon
        del self._iconSize
        del self._spacing

        self._iconWidget: SideBarIcon = SideBarIcon(icon=icon, iconSize=iconSize, parent=self)
        self._textWidget: SideBarText = SideBarText(text=text, parent=self)

        layout: QBoxLayout = newLayout(QBoxLayout, spacing=spacing, margins=(6, 4, 6, 4))
        self.setLayout(layout)
        self._layout = layout

        self._rebuildLayout()
        self._applyStateProperties()

    # ==================================================================================
    def setCallback(self, callback: Optional[Callable]) -> None:
        self._callback = callback

    # ==================================================================================
    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: UUID | str) -> None:
        self._id = str(value)

    @property
    def text(self) -> str:
        return self._textWidget.Text

    @text.setter
    def text(self, value: str) -> None:
        self._textWidget.Text = value

    @property
    def iconSize(self) -> int:
        return self._iconWidget.iconSize

    @iconSize.setter
    def iconSize(self, value: int) -> None:
        self._iconWidget.iconSize = value

    @property
    def depth(self) -> int:
        return self._depth

    @depth.setter
    def depth(self, value: int) -> None:
        lDepth: int = max(0, int(value))
        if lDepth == self._depth:
            return
        self._depth = lDepth
        self._applyStateProperties()

    @property
    def role(self) -> SideBarItemRole:
        return self._role

    @role.setter
    def role(self, value: SideBarItemRole) -> None:
        if value is self._role:
            return
        self._role = value
        self._applyStateProperties()

    @property
    def displayMode(self) -> SideBarItemDisplayMode:
        return self._displayMode

    @displayMode.setter
    def displayMode(self, value: SideBarItemDisplayMode) -> None:
        if value == self._displayMode:
            return
        self._displayMode = value
        self._rebuildLayout()

    @property
    def iconPosition(self) -> SideBarIconPosition:
        return self._iconPosition

    @iconPosition.setter
    def iconPosition(self, value: SideBarIconPosition) -> None:
        if value == self._iconPosition:
            return
        self._iconPosition = value
        self._rebuildLayout()

    @property
    def selected(self) -> bool:
        return self._selected

    @selected.setter
    def selected(self, value: bool) -> None:
        lValue: bool = bool(value)
        if lValue is self._selected:
            return
        self._selected = lValue
        self._applyStateProperties()

    @property
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, value: bool) -> None:
        lValue: bool = bool(value)
        if lValue is self._active:
            return
        self._active = lValue
        if lValue:
            self._selected = True
        self._applyStateProperties()

    @property
    def iconWidget(self) -> SideBarIcon:
        return self._iconWidget

    @property
    def textWidget(self) -> SideBarText:
        return self._textWidget

    # ==================================================================================
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

    # ==================================================================================
    def _applyStateProperties(self) -> None:
        self.setProperty("depth", str(self._depth))
        self.setProperty(
            "role",
            "header" if self._role is SideBarItemRole.Header else "leaf",
        )
        self.setProperty("selected", "true" if self._selected else "false")
        self.setProperty("active", "true" if self._active else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def _rebuildLayout(self) -> None:
        while self._layout.count():
            self._layout.takeAt(0)

        lShowIcon = self._displayMode in (
            SideBarItemDisplayMode.IconOnly,
            SideBarItemDisplayMode.IconAndText,
        )
        lShowText = self._displayMode in (
            SideBarItemDisplayMode.TextOnly,
            SideBarItemDisplayMode.IconAndText,
        )

        self._iconWidget.setVisible(lShowIcon)
        self._textWidget.setVisible(lShowText)

        if self._iconPosition in (SideBarIconPosition.Left, SideBarIconPosition.Right):
            self._layout.setDirection(QBoxLayout.Direction.LeftToRight)
        else:
            self._layout.setDirection(QBoxLayout.Direction.TopToBottom)

        if self._iconPosition in (SideBarIconPosition.Left, SideBarIconPosition.Top):
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
