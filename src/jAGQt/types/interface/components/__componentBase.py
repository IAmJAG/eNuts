# ==================================================================================
# src/jAGQt/types/interface/components/__componentBase.py
# ==================================================================================
from PySide6.QtCore import QMargins
from PySide6.QtWidgets import QBoxLayout, QWidget


# ==================================================================================
class iComponentBase:
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
