# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QBoxLayout, QSizePolicy, QStackedWidget, QWidget

# ==================================================================================
from jAGFx.workflow import workflow
from jAGQt.utilities import newLayout
from jAGQt.widgets.components import ComponentBase
from jAGQt.widgets.sideBar import SideBar

# ==================================================================================
QPolicy = QSizePolicy.Policy
QDirection = QBoxLayout.Direction
# ==================================================================================


# ==================================================================================
@workflow
class Workspace(QWidget, ComponentBase):
    OBJECT_NAME = "W_WORKSPACE"

    def __init__(self, title: str = "jAG Workspace", *args, **kwargs) -> None:
        lObjName: str = kwargs.pop("objectName", self.OBJECT_NAME)
        super().__init__(objectName=lObjName, *args, **kwargs)
        self._title: str = title

    def _wInitializeUI(self) -> None:        
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setSizePolicy(QPolicy.Expanding, QPolicy.Expanding)
        
        sideBar: SideBar = SideBar("jAG Workspace")
        layout: QBoxLayout = newLayout(
            QBoxLayout, spacing=0, margins=0, direction=QDirection.TopToBottom
        )
        layout.addWidget(sideBar)

        self.setLayout(layout)
