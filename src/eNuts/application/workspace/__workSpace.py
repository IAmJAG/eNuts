# ==================================================================================
from __future__ import annotations

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QBoxLayout, QSizePolicy, QStackedWidget, QWidget

# ==================================================================================
from jAGFx.workflow import workflow
from jAGQt.widgets.components import ComponentBase, ObjectName
from jAGQt.widgets.sideBar import SideBar

# ==================================================================================
QSPolicy = QSizePolicy.Policy
StyleBackground = Qt.WidgetAttribute.WA_StyledBackground
# ==================================================================================


# ==================================================================================
@workflow
class WorkSpace(ComponentBase, ObjectName, QWidget):
    OBJECT_NAME = "W_WORKSPACE"
    def __init__(self: QWidget, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)        

    def _wInitializeUI(self: QWidget) -> None:        
        self.setAttribute(StyleBackground, True)

        sideBar: SideBar = SideBar()
        stack: QStackedWidget = QStackedWidget()
        
        self.setStyle("QWidget { border: none; }")

        layout: QBoxLayout = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)        

        layout.addWidget(sideBar)
        layout.addWidget(stack, 1)

        if hasattr(self, "_layout"):
            self._layout = layout
            del self._layout
            
        self.setLayout(layout)
        
