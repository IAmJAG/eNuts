# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSizePolicy, QWidget

# ==================================================================================
from jAGFx.workflow import workflow

# ==================================================================================
QSPolicy = QSizePolicy.Policy
StyleBackground = Qt.WidgetAttribute.WA_StyledBackground
# ==================================================================================


# ==================================================================================
@workflow
class ObjectName:
    OBJECT_NAME = "W_OBJECTNAME"

    def __init__(self: QWidget, *args, **kwargs):
        OBJNAME: str = kwargs.pop("objectName", self.OBJECT_NAME)
        super().__init__(objectName=OBJNAME, *args, **kwargs)

    def _wInitializeUI(self: QWidget) -> None:
        self.setSizePolicy(QSPolicy.Expanding, QSPolicy.Expanding)
        self.setAttribute(StyleBackground, True)
