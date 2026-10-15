# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QBoxLayout, QMainWindow, QWidget

# ==================================================================================
from jAGFx.workflow import workflow

# ==================================================================================
from ...types.interface.window import iWindowBase
from ...widgets.components import ComponentBase, ObjectName


# ==================================================================================
@workflow("InitializeUI")
class WindowBase(QMainWindow, ObjectName, ComponentBase, iWindowBase):
    OBJECT_NAME = "W_WINDOW_BASE"
    def __init__(self, frameless: bool = False, *args, **kwargs):
        layout: QBoxLayout = kwargs.pop("layout", None)
        super().__init__(*args, **kwargs)        
        if frameless: self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self._layout: QBoxLayout = layout

    def _wInitializeUI(self) -> None:
        layout: QBoxLayout = self._layout if hasattr(self, "_layout") else None
        if layout is None:
            layout: QBoxLayout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
            layout.setSpacing(0)
            layout.setContentsMargins(0, 0, 0, 0)

        central: QWidget = self.centralWidget()
        if central is None: central: QWidget = QWidget(self)        
        central.setLayout(layout)
        self._layout: QBoxLayout = layout        
        



        

        
