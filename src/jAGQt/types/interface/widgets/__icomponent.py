# ==================================================================================
# src/jAGQt/types/interface/widgets/__icomponent.py
# ==================================================================================
from PySide6.QtCore import QMargins
from PySide6.QtWidgets import QBoxLayout, QWidget


# ==================================================================================
class icomponent:
    @property
    def Name(self: QWidget) -> str: ...
    @property
    def Parent(self: QWidget) -> QWidget: ...    
    @property
    def Layout(self: QWidget) -> QBoxLayout: ...
    @property
    def ContentSpacing(self: QWidget): ...
    @property
    def ContentMargins(self: QWidget) -> QMargins: ...
