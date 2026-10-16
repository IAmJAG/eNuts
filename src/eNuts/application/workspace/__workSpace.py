# ==================================================================================
from __future__ import annotations

# ==================================================================================
from traceback import format_exc

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QBoxLayout, QSizePolicy, QStackedWidget, QWidget

# ==================================================================================
from jAGFx.workflow import workflow
from jAGQt.widgets.components import ComponentBase, ObjectName
from jAGQt.widgets.sideBar import SideBar, eSideBarState
from utilities.io import getICONPath

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
        try:
            super().__init__(*args, **kwargs)
        except Exception as ex:
            error("[WorkSpace] __init__ FAIL", ex)
            error(f"[WorkSpace] __init__ traceback:\n{format_exc()}")
            raise
        verbose(f"[WorkSpace] __init__ EXIT objectName={self.objectName()!r}")

    def _wInitializeUI(self: QWidget) -> None:
        verbose("[WorkSpace] _wInitializeUI ENTER")
        try:
            self.setAttribute(StyleBackground, True)
            # DEV visibility: distinct background so the workspace area is obvious
            self.setStyleSheet("background-color: #1e1e1e;")

            expandPath: str = getICONPath("expand.png")
            collapsePath: str = getICONPath("collapse.png")
            verbose(
                f"[WorkSpace] SideBar icons expand={expandPath!r} collapse={collapsePath!r}"
            )

            sideBar: SideBar = SideBar(
                icons={
                    eSideBarState.Expanded: expandPath,
                    eSideBarState.Collapsed: collapsePath,
                },
                title="eNuts",
            )
            verbose(
                f"[WorkSpace] SideBar created objectName={sideBar.objectName()!r} "
                f"state={sideBar.State!r}"
            )

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
        except Exception as ex:
            error("[WorkSpace] _wInitializeUI FAIL", ex)
            error(f"[WorkSpace] _wInitializeUI traceback:\n{format_exc()}")
            raise
