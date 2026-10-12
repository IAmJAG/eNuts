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
from jAGQt.animations import LightningShootAnimation, RubberBandAnimation
from jAGQt.types import DockPosition

# ==================================================================================
from ...utilities import newLayout
from ..components import ComponentBase

# ==================================================================================
from .__options import sideBarConfig
from .components import (
    DockControl,
    ItemDisplayMode,
    ItemRole,
    SeparatorType,
    SideBarContent,
    SideBarGroup,
    SideBarHeader,
    SideBarSeparator,
    SideBarText,
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

        mainLayout: QBoxLayout = newLayout(QBoxLayout, spacing=0, margins=0)
        mainLayout.setDirection(QBoxLayout.Direction.TopToBottom)
        mainLayout.addWidget(header)        
        self.setLayout(mainLayout)

        self._header: SideBarHeader = SideBarHeader(
            title=title, iconSize=self._config.iconSize,
        )

    @property
    def config(self) -> sideBarConfig:
        return self._config