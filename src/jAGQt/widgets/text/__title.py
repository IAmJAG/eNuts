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
class Title(Text):
    OBJECT_NAME = "W_TITLE"
    def __init__(self, title: str, *args, **kwargs) -> None:
        lObjName: str = kwargs.pop("objectName", self.OBJECT_NAME)
        super().__init__(text=title, objectName=lObjName, *args, **kwargs)
        self.setSizePolicy(QPolicy.Expanding, QPolicy.Fixed)

