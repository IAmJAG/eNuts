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
        del self._title
        del self._description

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

        # Do not call setVisible here. Header may still be top-level during Page build;
        # effective visibility follows the parent chain once the page is shown.
        # Hide empty description only via the flag after parenting is stable:
        if not descriptionText:
            description.hide()

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
