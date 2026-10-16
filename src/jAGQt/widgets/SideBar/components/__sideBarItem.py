# ==================================================================================
from __future__ import annotations

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QBoxLayout, QSizePolicy, QWidget

# ==================================================================================
from jAGFx.workflow import workflow

# ==================================================================================
from ....utilities import newLayout
from ...components import ComponentBase, ObjectName

# ==================================================================================
QSPolicy = QSizePolicy.Policy
StyleBackground = Qt.WidgetAttribute.WA_StyledBackground
# ==================================================================================


# ==================================================================================
@workflow
class SideBarItem(ComponentBase, ObjectName, QWidget):
    OBJECT_NAME = "W_SIDEBAR_ITEM"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def _wInitializeUI(self) -> None:
        self.setAttribute(StyleBackground, True)
        self.setSizePolicy(QSPolicy.Expanding, QSPolicy.Fixed)

        outerLayout: QBoxLayout = newLayout(
            QBoxLayout,
            spacing=8,
            margins=(8, 8, 8, 8),
            direction=QBoxLayout.Direction.LeftToRight,
        )
        textColumn: QBoxLayout = newLayout(
            QBoxLayout,
            spacing=0,
            margins=(0, 0, 0, 0),
            direction=QBoxLayout.Direction.TopToBottom,
        )
        outerLayout.addLayout(textColumn, stretch=1)

        self.setLayout(outerLayout)
        self._layout: QBoxLayout = outerLayout
        self._textColumn: QBoxLayout = textColumn

    def _addLeading(self, widget: QWidget) -> None:
        self._layout.insertWidget(0, widget, stretch=0)

    def _addTextWidget(self, widget: QWidget) -> None:
        self._textColumn.addWidget(widget)
