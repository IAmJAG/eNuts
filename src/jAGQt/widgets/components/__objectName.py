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
        verbose(f"[ObjectName] __init__ ENTER objectName={OBJNAME!r} cls={type(self).__name__}")
        super().__init__(objectName=OBJNAME, *args, **kwargs)
        verbose(f"[ObjectName] __init__ EXIT objectName={self.objectName()!r}")

    def _wInitializeUI(self: QWidget) -> None:
        verbose(f"[ObjectName] _wInitializeUI ENTER cls={type(self).__name__} objectName={self.objectName()!r}")
        self.setSizePolicy(QSPolicy.Expanding, QSPolicy.Expanding)
        self.setAttribute(StyleBackground, True)
        verbose(f"[ObjectName] _wInitializeUI EXIT cls={type(self).__name__}")
