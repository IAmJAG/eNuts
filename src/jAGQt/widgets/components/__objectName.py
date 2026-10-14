# ==================================================================================
from PySide6.QtWidgets import QWidget


# ==================================================================================
class ObjectName:
    OBJECT_NAME = "W_OBJECTNAME"
    def __init__(self: QWidget, *args, **kwargs):
        OBJNAME: str = kwargs.pop("objectName", self.OBJECT_NAME)
        super().__init__(objectName=OBJNAME, *args, **kwargs)
