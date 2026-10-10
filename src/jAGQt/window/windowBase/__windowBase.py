# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QBoxLayout, QMainWindow, QWidget

# ==================================================================================
from jAGFx.names import getRandomName
from jAGFx.workflow import workflow

# ==================================================================================
from ...widgets.components import ComponentBase


# ==================================================================================
@workflow("InitializeUI")
class WindowBase(QMainWindow, ComponentBase):
    def __init__(self, name: str = None, frameless: bool = False, *args, **kwargs):
        self._layout: QBoxLayout = kwargs.pop("layout", None)
        
        super().__init__(*args, **kwargs)
        if frameless: self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.Name = name if name else getRandomName()

    def _wInitializeUI(self) -> None:
        central: QWidget = self.centralWidget()
        if central is None:
            central = QWidget(self)
            self.setCentralWidget(central)

        if self._layout is None:
            self._layout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
            self.ContentSpacing = 0
            self.ContentMargins = 0

        central.setLayout(self._layout)
