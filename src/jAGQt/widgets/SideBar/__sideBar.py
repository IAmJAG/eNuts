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
        verbose("[SideBar] __init__ ENTER")
        super().__init__(*args, **kwargs)
        verbose(f"[SideBar] __init__ EXIT objectName={self.objectName()!r}")

    def _wInitializeUI(self) -> None:
        verbose("[SideBar] _wInitializeUI ENTER")
        self.setSizePolicy(QSPolicy.Fixed, QSPolicy.Expanding)
        # DEV visibility: fixed width + solid background so the sidebar is obvious
        self.setFixedWidth(200)
        self.setStyleSheet("background-color: #333337; border-right: 1px solid #3c3c3c;")
        verbose(
            f"[SideBar] _wInitializeUI EXIT "
            f"fixedWidth={self.width()} sizePolicy={self.sizePolicy().horizontalPolicy()}"
        )
