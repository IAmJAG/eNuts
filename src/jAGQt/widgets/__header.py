# ==================================================================================
# src/jAGQt/widgets/workspace/__page.py
# ==================================================================================
from typing import Optional
from uuid import UUID, uuid4

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QBoxLayout,
    QFrame,
    QLabel,
    QSizePolicy,
    QWidget,
)

from jAGFx.workflow import workflow

# ==================================================================================
from ..utilities import newLayout
from .components import ComponentBase


# ==================================================================================
@workflow("InitializeUI")
class Header(QFrame, ComponentBase):
    OBJECT_NAME = "W_HEADER"
    def __init__( self,
        title: str = "jAGQt Page", description: str = "",
        id: Optional[str] = None, *args, **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._title = title
        self._description = description
        
    def _wInitializeUI(self):
        objName: str = self.OBJECT_NAME        
        self.setObjectName(objName)        
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        titleText: str = self._title
        descriptionText: str = self._description

        title: QLabel = QLabel(titleText)
        title.setObjectName(f"{objName}_TITLE")
        title.setVisible(bool(title))

        description: QLabel = QLabel(descriptionText)
        description.setObjectName(f"{objName}_DESCRIPTION")
        description.setVisible(bool(description))

        outerLayout: QBoxLayout = newLayout(QBoxLayout, spacing=0, margins=(0, 0, 0, 0), direction=QBoxLayout.Direction.TopToBottom)

        outerLayout.addWidget(title)
        outerLayout.addWidget(description)

        self._title: QLabel = title
        self._description: QLabel = description

    # ==================================================================================
    @property
    def Title(self) -> str:
        return self._title.text()

    @Title.setter
    def Title(self, value: str) -> None:
        self._title.setText(value)

    @property
    def Description(self) -> str:
        return self._description

    @Description.setter
    def Description(self, value: str) -> None:
        self._description.setText(value)