# ==================================================================================
# src/jAGQt/types/interface/window/windowBase/__windowBase.py
# ==================================================================================
from PySide6.QtWidgets import QBoxLayout


# ==================================================================================
class iWindowBase:
    def __init__(self, name: str = None, frameless: bool = False, *args, **kwargs): ...
    @property
    def Name(self) -> str: ...
    @property
    def Layout(self) -> QBoxLayout: ...
