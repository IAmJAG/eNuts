# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QBoxLayout, QSizePolicy, QWidget

# ==================================================================================
from jAGFx.workflow import workflow

# ==================================================================================
from ...utilities import newLayout
from ..components import ComponentBase
from ..text import Title
from .components import SideBarHeader
from .types import sideBarConfig


# ==================================================================================
@workflow
class SideBar(QWidget, ComponentBase):
    OBJECT_NAME = "W_SIDEBAR"
    def __init__(
        self, title: str = "", description: str = "", config: Optional[sideBarConfig] = None, *args, **kwargs,
    ) -> None:
        OBJNAME: str = kwargs.pop("objectName", self.OBJECT_NAME)
        super().__init__(objectName=OBJNAME, *args, **kwargs)
        self._title: str = title
        self._description: str = description
        self._config: sideBarConfig = config if config is not None else sideBarConfig()

    def _wInitializeUI(self) -> None:
        title: str = self._title
        description: str = self._description

        del self._title
        del self._description

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        header: SideBarHeader = SideBarHeader(title)
        # header.setStyleSheet("background-color: white; color: black;")
        content: QWidget = QWidget()

        layout: QBoxLayout = newLayout(QBoxLayout, spacing=0, margins=0, direction=QBoxLayout.Direction.TopToBottom)
        layout.addWidget(header)
        layout.addWidget(content, 1)

        self.setLayout(layout)

    @property
    def config(self) -> sideBarConfig:
        return self._config