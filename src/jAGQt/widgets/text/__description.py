# ==================================================================================
from __future__ import annotations

# ==================================================================================
from PySide6.QtWidgets import QSizePolicy

# ==================================================================================
from jAGFx.workflow import workflow

# ==================================================================================
from .__text import Text

# ==================================================================================
QPolicy = QSizePolicy.Policy
# ==================================================================================


# ==================================================================================
@workflow
class Description(Text):
    OBJECT_NAME = "W_DESCRIPTION"
    def __init__(self, text: str, *args, **kwargs) -> None:
        lObjName: str = kwargs.pop("objectName", self.OBJECT_NAME)        
        super().__init__(text=text, objectName=lObjName, wordWrap=True, *args, **kwargs)
        self.setSizePolicy(QPolicy.Expanding, QPolicy.Preferred)