# ==================================================================================
# src/jAGQt/window/windowBase/__windowBase.py
# ==================================================================================
# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QBoxLayout, QMainWindow, QWidget

from jAGFx.names import getRandomName
from jAGFx.workflow import workflow

# ==================================================================================
from ...widgets.components import component


# ==================================================================================
@workflow("InitializeUI")
class WindowBase(component, QMainWindow):
    """Generic jAGQt foundation for application windows."""

    def __init__(self, name: str = None, frameless: bool = False, *args, **kwargs):
        self._layout: QBoxLayout = kwargs.pop("layout", None)
        super().__init__(*args, **kwargs)
        self._frameless = frameless
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

        if self._frameless:
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)

    @property
    def Name(self) -> str:
        return self.objectName()

    @Name.setter
    def Name(self, value: str):
        self.setObjectName(value)

    @property
    def Layout(self) -> QBoxLayout:
        return self.centralWidget().layout()

    @Layout.setter
    def Layout(self, value: QBoxLayout):
        self.centralWidget().setLayout(value)
