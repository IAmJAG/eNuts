# ==================================================================================
# src/jAGQt/widgets/workspace/components/__commandBarGroup.py
# ==================================================================================
from typing import Dict

# ==================================================================================
from PySide6.QtWidgets import QWidget

# ==================================================================================
from jAGFx.workflow import workflow

# ==================================================================================
from ...types.interface.widgets.commandBar import iCommandBarButton
from ...widgets.components import ComponentBase
from .__base import _commandBarBase


# ==================================================================================
@workflow("InitializeBase")
class CommandBarGroup(QWidget, ComponentBase, _commandBarBase):
    OBJECT_NAME = "C_COMMANDBAR_GROUP"
    def __init__(self, name: str, *args, **kwargs) -> None:
        OBJNAME: str = kwargs.pop("objectName", self.OBJECT_NAME)
        super().__init__(objectName=OBJNAME, *args, **kwargs)
        self._buttons: Dict[str, iCommandBarButton] = dict[str, iCommandBarButton]()
        self._name: str = name
