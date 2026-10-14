# ==================================================================================
from __future__ import annotations

# ==================================================================================
from PySide6.QtWidgets import QMainWindow, QWidget

# ==================================================================================
from jAGFx.workflow import workflow
from jAGQt.widgets.components import ComponentBase, ObjectName


# ==================================================================================
@workflow
class WorkSpace(QWidget, ObjectName, ComponentBase):
    OBJECT_NAME = "W_WORKSPACE"
    def __init__(self: QWidget, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def _wInitializeUI(self: QWidget) -> None:
        print(f"[WorkSpace] objectName={self.objectName()}", flush=True)
