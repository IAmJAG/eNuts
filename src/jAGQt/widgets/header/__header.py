# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional, Union

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QPixmap, QResizeEvent
from PySide6.QtWidgets import QBoxLayout, QHBoxLayout, QSizePolicy, QVBoxLayout, QWidget

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
        title: str = "", description: Optional[str] = "",
        icon: Optional[Union[QIcon, QPixmap, str]] = None,
        iconPosition: IconPosition = IconPosition.TitleRow,
        iconSize: int = 24,
        iconBG: Optional[Union[str, QColor]] = None,
        iconFG: Optional[Union[str, QColor]] = None,        
        *args, **kwargs,
    ) -> None:
        lObjName: str = kwargs.pop("objectName", self.OBJECT_NAME)
        super().__init__(objectName=lObjName, *args, **kwargs)

        self._titleText: str = title
        self._descriptionText: str = description or ""
        self._iconData: Optional[Union[QIcon, QPixmap, str]] = icon
        self._iconPosition: IconPosition = iconPosition
        self._iconBG: Optional[Union[str, QColor]] = iconBG or QColor(Qt.GlobalColor.transparent)
        self._iconFG: Optional[Union[str, QColor]] = iconFG or Qt.GlobalColor.darkGray
        self._iconSize: int = iconSize
        
    def _wInitializeUI(self, rebuild: bool = True) -> None:
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)        
        
        # Instantiate widgets using the attached component classes
        title: Title = Title(self._titleText)
        self.setFixedHeight(50)
        description: Description = Description(self._descriptionText)

        iconBG: QColor = QColor(self._iconBG)
        iconFG: QColor = QColor(self._iconFG)
        icon: Icon = Icon(self._iconData, background=iconBG, foreground=iconFG)
        icon.setSizePolicy(QPolicy.Fixed, QPolicy.Fixed)

        del self._titleText
        del self._descriptionText
        del self._iconData
        del self._iconBG
        del self._iconFG

        self._title = title
        self._description = description
        self._icon: icon = icon
        self.setLayout(newLayout(QVBoxLayout, spacing=0, margins=0))

        if rebuild:
            self._rebuildLayout()

    # ==================================================================================
    def _clearLayout(self) -> None:
        layout: QBoxLayout = self.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item is None: continue
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

    def _rebuildLayout(self) -> None:
        icon: Icon = self._icon
        title: Title = self._title
        description: Description = self._description
        iconPosition: IconPosition = self._iconPosition

        hasIcon: bool = icon is not None and isinstance(icon, Icon)                
        rowLayout: QBoxLayout = newLayout(QHBoxLayout, spacing=8, margins=0)
        mainLayout: QBoxLayout = self.layout()
        self._clearLayout()

        if iconPosition == IconPosition.TitleRow:                        
            iconSize: int = title.size().height()
            icon.setFixedSize(iconSize, iconSize)           

            rowLayout.setDirection(QBoxDirection.LeftToRight)
            if hasIcon: rowLayout.addWidget(icon)
            rowLayout.addWidget(title, 1)

            mainLayout.addLayout(rowLayout)
            mainLayout.addWidget(description)

        elif iconPosition in [IconPosition.Left, IconPosition.Right]:            
            iconSize: int = title.size().height() + description.size().height()
            icon.setFixedSize(iconSize, iconSize)
            
            titleColLayout: QBoxLayout = newLayout(QVBoxLayout, spacing=0, margins=0, direction=QBoxDirection.TopToBottom)
            titleColLayout.addWidget(title)
            titleColLayout.addWidget(description)

            rowLayout.setDirection(QBoxDirection.LeftToRight)
            if hasIcon: rowLayout.addWidget(icon)
            rowLayout.addLayout(titleColLayout, 1)            
            mainLayout.addLayout(rowLayout)
        else:
            iconSize: int = self._iconSize
            icon.setFixedSize(iconSize, iconSize)
            if iconPosition == IconPosition.Top:
                if hasIcon: mainLayout.addWidget(icon)
                mainLayout.addWidget(title)
                mainLayout.addWidget(description)

            elif iconPosition == IconPosition.Bottom:
                mainLayout.addWidget(title)
                mainLayout.addWidget(description)
                if hasIcon: mainLayout.addWidget(icon)        
    
    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)

    @property
    def title(self) -> str:
        return self._title.Text if self._title and isinstance(self._title, Title) else ""

    @title.setter
    def title(self, value: str) -> None:
        if self._title:
            self._title.setText(value)
            self._title.setVisible(bool(value))            
            self._rebuildLayout()

    @property
    def description(self) -> str:
        description: Description = self._description
        return description.Text if description and isinstance(description, Description) else ""

    @description.setter
    def description(self, value: str) -> None:
        if self._description:
            self._description.setText(value)
            self._description.setVisible(bool(value))
            self._rebuildLayout()

    @property
    def icon(self) -> Optional[Union[QIcon, QPixmap]]:
        return self._icon.icon if self._icon and isinstance(self._icon, Icon) else None

    @icon.setter
    def icon(self, value: Optional[Union[QIcon, QPixmap, str]]) -> None:
        if self._icon:
            self._icon.setIcon(value)
            self._rebuildLayout()

    @property
    def iconPosition(self) -> IconPosition:
        return self._iconPosition

    @iconPosition.setter
    def iconPosition(self, value: IconPosition) -> None:
        if value is self._iconPosition: return
        self._iconPosition = value
        self._rebuildLayout()
