# ==================================================================================
# src/jAGQt/window/windowBase/__windowBase.py
# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QBoxLayout, QMainWindow, QWidget

# ==================================================================================
from jAGFx.names import getRandomName
from jAGFx.workflow import workflow

# ==================================================================================
from ...types.components import ComponentBase


# ==================================================================================
@workflow("InitializeUI")
class WindowBase(QMainWindow, ComponentBase):
    def __init__(self, name: str = None, frameless: bool = False, *args, **kwargs):
        self._layout: QBoxLayout = kwargs.pop("layout", None)
        
        super().__init__(*args, **kwargs)        
        if frameless:
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self.Name = name if name else getRandomName()

    def _wInitializeUI(self) -> None:
        if self.centralWidget() is None:
            self.setCentralWidget(QWidget())

        if self._layout is None:
            self.Layout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
            self.ContentSpacing = 0
            self.ContentMargins = 0
            
        else:
            self.Layout = self._layout

        

        
