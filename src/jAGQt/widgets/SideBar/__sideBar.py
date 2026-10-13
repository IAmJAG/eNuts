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
from .types import sideBarConfig


# ==================================================================================
@workflow
class SideBar(QWidget, ComponentBase):
    OBJECT_NAME = "W_SIDEBAR"
    def __init__(
        self, title: str = "", config: Optional[sideBarConfig] = None, *args, **kwargs,
    ) -> None:
        OBJNAME: str = kwargs.pop("objectName", self.OBJECT_NAME)
        super().__init__(objectName=OBJNAME, *args, **kwargs)

    def _wInitializeUI(self) -> None:
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        text: Title = Title("jAG QT")

        layout: QBoxLayout = newLayout(QBoxLayout, spacing=0, margins=0, direction=QBoxLayout.Direction.TopToBottom)
        layout.addWidget(text)

        self.setLayout(layout)
        