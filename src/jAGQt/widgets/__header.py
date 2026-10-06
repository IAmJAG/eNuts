# ==================================================================================
# src/jAGQt/widgets/__header.py
# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QBoxLayout,
    QFrame,
    QLabel,
)

from jAGFx.workflow import workflow

# ==================================================================================
from ..utilities import newLayout
from .components import ComponentBase


# ==================================================================================
@workflow("InitializeUI")
class Header(QFrame, ComponentBase):
    OBJECT_NAME = "W_HEADER"

    def __init__(
        self,
        title: str = "jAGQt Page",
        description: str = "",
        id: Optional[str] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._title = title
        self._description = description

    def _wInitializeUI(self) -> None:
        objName: str = self.OBJECT_NAME
        self.setObjectName(objName)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        titleText: str = self._title
        descriptionText: str = self._description

        # Build first; do NOT setVisible while parentless — that opens top-level windows.
        # Layout.addWidget + setLayout reparents; visibility is applied only after that.
        title: QLabel = QLabel(titleText)
        title.setObjectName(f"{objName}_TITLE")

        description: QLabel = QLabel(descriptionText)
        description.setObjectName(f"{objName}_DESCRIPTION")

        outerLayout: QBoxLayout = newLayout(
            QBoxLayout,
            spacing=0,
            margins=(0, 0, 0, 0),
            direction=QBoxLayout.Direction.TopToBottom,
        )
        outerLayout.addWidget(title)
        outerLayout.addWidget(description)

        self.setLayout(outerLayout)
        self._layout: QBoxLayout = outerLayout
        self._title: QLabel = title
        self._description: QLabel = description

        # Safe now: labels are children of Header via the layout.
        title.setVisible(bool(titleText))
        description.setVisible(bool(descriptionText))

    # ==================================================================================
    @property
    def Title(self) -> str:
        return self._title.text()

    @Title.setter
    def Title(self, value: str) -> None:
        self._title.setText(value)
        self._title.setVisible(bool(value))

    @property
    def Description(self) -> str:
        return self._description.text()

    @Description.setter
    def Description(self, value: str) -> None:
        self._description.setText(value)
        self._description.setVisible(bool(value))
