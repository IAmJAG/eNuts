# ==================================================================================
from PySide6.QtWidgets import QSizePolicy, QWidget

# ==================================================================================
from jAGFx.workflow import workflow

# ==================================================================================
from ..components import ComponentBase, ObjectName

# ==================================================================================
QSPolicy = QSizePolicy.Policy
# ==================================================================================

# ==================================================================================
@workflow
class SideBar(ComponentBase, ObjectName, QWidget):
    OBJECT_NAME = "W_SIDEBAR"
    def __init__(self, *args, **kwargs) -> None:        
        super().__init__(*args, **kwargs)

    def _wInitializeUI(self) -> None:
        self.setSizePolicy(QSPolicy.Fixed, QSPolicy.Expanding)
        pass