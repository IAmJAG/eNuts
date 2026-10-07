# ==================================================================================
from PySide6.QtWidgets import QWidget

# ==================================================================================
from ..components import ComponentBase


# ==================================================================================
class SideBar(QWidget, ComponentBase): 
    def __init__(self, title: str = "", *args, **kwargs) -> None: ...