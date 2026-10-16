# ==================================================================================
from __future__ import annotations

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QBoxLayout, QSizePolicy, QStackedWidget, QWidget

# ==================================================================================
from jAGFx.workflow import workflow
from jAGQt.widgets.components import ComponentBase, ObjectName
from jAGQt.widgets.sideBar import SideBar

# ==================================================================================
QSPolicy = QSizePolicy.Policy
StyleBackground = Qt.WidgetAttribute.WA_StyledBackground
# ==================================================================================


# ==================================================================================
@workflow
class WorkSpace(ComponentBase, ObjectName, QWidget):
    OBJECT_NAME = "W_WORKSPACE"

    def __init__(self: QWidget, *args, **kwargs) -> None:
        verbose("[WorkSpace] __init__ ENTER")
        super().__init__(*args, **kwargs)
        verbose(f"[WorkSpace] __init__ EXIT objectName={self.objectName()!r}")

    def _wInitializeUI(self: QWidget) -> None:
        verbose("[WorkSpace] _wInitializeUI ENTER")
        self.setAttribute(StyleBackground, True)
        # DEV visibility: distinct background so the workspace area is obvious
        self.setStyleSheet("background-color: #1e1e1e;")

        sideBar: SideBar = SideBar()
        verbose(f"[WorkSpace] SideBar created objectName={sideBar.objectName()!r}")

        stack: QStackedWidget = QStackedWidget()
        stack.setObjectName("W_WORKSPACE_STACK")
        # DEV visibility: contrasting stack area
        stack.setStyleSheet("background-color: #252526;")
        stack.setSizePolicy(QSPolicy.Expanding, QSPolicy.Expanding)

        layout: QBoxLayout = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(sideBar)
        layout.addWidget(stack, 1)

        if hasattr(self, "_layout"):
            self._layout = layout
            del self._layout

        self.setLayout(layout)
        verbose(
            f"[WorkSpace] _wInitializeUI EXIT "
            f"sideBar.sizeHint={sideBar.sizeHint()} "
            f"layoutCount={layout.count()}"
        )
