# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional, Union

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QPixmap, QResizeEvent
from PySide6.QtWidgets import QBoxLayout, QSizePolicy, QWidget

# ==================================================================================
from jAGFx.workflow import workflow

# ==================================================================================
from ...utilities import newLayout
from ..components import ComponentBase
from ..icon import Icon
from ..text import Description, Title
from .__iconPosition import IconPosition

# ==================================================================================
QBoxDirection = QBoxLayout.Direction
QPolicy = QSizePolicy.Policy
# ==================================================================================


# ==================================================================================
@workflow("InitializeUI")
class Header(QWidget, ComponentBase):
    OBJECT_NAME = "W_HEADER"

    def __init__(
        self,
        title: str = "",
        description: Optional[str] = "",
        icon: Optional[Union[QIcon, QPixmap, str]] = None,
        *args,
        **kwargs,
    ) -> None:
        lObjName: str = kwargs.pop("objectName", self.OBJECT_NAME)
        super().__init__(objectName=lObjName, *args, **kwargs)

        self._titleText: str = title
        self._descriptionText: str = description or ""
        self._iconData: Optional[Union[QIcon, QPixmap, str]] = icon
        # Defaults — settable after construction via properties
        self._iconPosition: IconPosition = IconPosition.TitleRow
        self._iconSize: int = 24
        self._iconBG: QColor = QColor(Qt.GlobalColor.transparent)
        self._iconFG: QColor = QColor(Qt.GlobalColor.darkGray)

    def _wInitializeUI(self, rebuild: bool = True) -> None:
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        title: Title = Title(self._titleText)
        description: Description = Description(self._descriptionText)

        icon: Icon = Icon(
            self._iconData,
            background=self._iconBG,
            foreground=self._iconFG,
        )
        icon.setSizePolicy(QPolicy.Fixed, QPolicy.Fixed)

        del self._titleText
        del self._descriptionText
        del self._iconData

        self._title = title
        self._description = description
        self._icon: Icon = icon
        # QBoxLayout only — QVBoxLayout/QHBoxLayout reject Direction in __init__.
        self.setLayout(
            newLayout(
                QBoxLayout,
                spacing=0,
                margins=0,
                direction=QBoxDirection.TopToBottom,
            )
        )

        if rebuild:
            self._rebuildLayout()

    def _clearLayout(self) -> None:
        layout = self.layout()
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            if item is None:
                continue
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
            childLayout = item.layout()
            if childLayout is not None:
                childLayout.setParent(None)

    def _rebuildLayout(self) -> None:
        icon: Icon = self._icon
        title: Title = self._title
        description: Description = self._description
        iconPosition: IconPosition = self._iconPosition

        hasIcon: bool = icon is not None and isinstance(icon, Icon) and icon.icon is not None
        rowLayout: QBoxLayout = newLayout(
            QBoxLayout,
            spacing=8,
            margins=0,
            direction=QBoxDirection.LeftToRight,
        )
        mainLayout = self.layout()
        if mainLayout is None:
            return
        self._clearLayout()

        if iconPosition == IconPosition.TitleRow:
            iconSize: int = max(title.sizeHint().height(), self._iconSize)
            icon.setFixedSize(iconSize, iconSize)

            if hasIcon:
                rowLayout.addWidget(icon)
            rowLayout.addWidget(title, 1)

            mainLayout.addLayout(rowLayout)
            mainLayout.addWidget(description)

        elif iconPosition in (IconPosition.Left, IconPosition.Right):
            iconSize = max(
                title.sizeHint().height() + description.sizeHint().height(),
                self._iconSize,
            )
            icon.setFixedSize(iconSize, iconSize)

            titleColLayout: QBoxLayout = newLayout(
                QBoxLayout,
                spacing=0,
                margins=0,
                direction=QBoxDirection.TopToBottom,
            )
            titleColLayout.addWidget(title)
            titleColLayout.addWidget(description)

            if iconPosition == IconPosition.Left and hasIcon:
                rowLayout.addWidget(icon)
            rowLayout.addLayout(titleColLayout, 1)
            if iconPosition == IconPosition.Right and hasIcon:
                rowLayout.addWidget(icon)
            mainLayout.addLayout(rowLayout)

        else:
            iconSize = self._iconSize
            icon.setFixedSize(iconSize, iconSize)
            if iconPosition == IconPosition.Top:
                if hasIcon:
                    mainLayout.addWidget(icon)
                mainLayout.addWidget(title)
                mainLayout.addWidget(description)
            elif iconPosition == IconPosition.Bottom:
                mainLayout.addWidget(title)
                mainLayout.addWidget(description)
                if hasIcon:
                    mainLayout.addWidget(icon)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)

    # ---- lowercase API -----------------------------------------------------------
    @property
    def title(self) -> str:
        return self.Title

    @title.setter
    def title(self, value: str) -> None:
        self.Title = value

    @property
    def description(self) -> str:
        return self.Description

    @description.setter
    def description(self, value: str) -> None:
        self.Description = value

    # ---- Page-facing Title / Description -----------------------------------------
    @property
    def Title(self) -> str:
        return self._title.Text if self._title and isinstance(self._title, Title) else ""

    @Title.setter
    def Title(self, value: str) -> None:
        if self._title:
            self._title.Text = value
            self._title.setVisible(bool(value))
            self._rebuildLayout()

    @property
    def Description(self) -> str:
        description: Description = self._description
        return (
            description.Text
            if description and isinstance(description, Description)
            else ""
        )

    @Description.setter
    def Description(self, value: str) -> None:
        if self._description:
            self._description.Text = value
            self._description.setVisible(bool(value))
            self._rebuildLayout()

    # ---- Icon & layout properties ------------------------------------------------
    @property
    def Icon(self) -> Optional[Union[QIcon, QPixmap]]:
        return self._icon.icon if self._icon and isinstance(self._icon, Icon) else None

    @Icon.setter
    def Icon(self, value: Optional[Union[QIcon, QPixmap, str]]) -> None:
        if self._icon:
            self._icon.setIcon(value)
            self._rebuildLayout()

    @property
    def icon(self) -> Optional[Union[QIcon, QPixmap]]:
        return self.Icon

    @icon.setter
    def icon(self, value: Optional[Union[QIcon, QPixmap, str]]) -> None:
        self.Icon = value

    @property
    def IconPosition(self) -> IconPosition:
        return self._iconPosition

    @IconPosition.setter
    def IconPosition(self, value: IconPosition) -> None:
        if value is self._iconPosition:
            return
        self._iconPosition = value
        self._rebuildLayout()

    @property
    def iconPosition(self) -> IconPosition:
        return self.IconPosition

    @iconPosition.setter
    def iconPosition(self, value: IconPosition) -> None:
        self.IconPosition = value

    @property
    def IconSize(self) -> int:
        return self._iconSize

    @IconSize.setter
    def IconSize(self, value: int) -> None:
        if value == self._iconSize:
            return
        self._iconSize = max(1, int(value))
        self._rebuildLayout()

    @property
    def iconSize(self) -> int:
        return self.IconSize

    @iconSize.setter
    def iconSize(self, value: int) -> None:
        self.IconSize = value

    @property
    def IconBackground(self) -> QColor:
        return self._iconBG

    @IconBackground.setter
    def IconBackground(self, value: Optional[Union[str, QColor]]) -> None:
        if isinstance(value, str):
            self._iconBG = QColor(value)
        elif isinstance(value, QColor):
            self._iconBG = value
        else:
            self._iconBG = QColor(Qt.GlobalColor.transparent)
        if self._icon:
            self._icon.setBackground(self._iconBG)
            self._rebuildLayout()

    @property
    def IconForeground(self) -> QColor:
        return self._iconFG

    @IconForeground.setter
    def IconForeground(self, value: Optional[Union[str, QColor]]) -> None:
        if isinstance(value, str):
            self._iconFG = QColor(value)
        elif isinstance(value, QColor):
            self._iconFG = value
        else:
            self._iconFG = QColor(Qt.GlobalColor.darkGray)
        if self._icon:
            self._icon.setForeground(self._iconFG)
            self._rebuildLayout()
