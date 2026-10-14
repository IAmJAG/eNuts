# ==================================================================================
from PySide6.QtWidgets import QWidget

# ==================================================================================
from jAGFx.workflow import workflow

# ==================================================================================
from ..components import ComponentBase, ObjectName


# ==================================================================================
@workflow
class SideBar(QWidget, ObjectName, ComponentBase):
    OBJECT_NAME = "W_SIDEBAR"
    def __init__(self, *args, **kwargs) -> None:        
        super().__init__(*args, **kwargs)

    def _wInitializeUI(self) -> None:
        print(f"[SideBar] objectName={self.objectName()}", flush=True)
        pass