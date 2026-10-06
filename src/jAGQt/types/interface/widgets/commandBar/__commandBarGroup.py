# ==================================================================================
# src/jAGQt/types/interface/widgets/commandBar/__commandBarGroup.py
# ==================================================================================
from PySide6.QtWidgets import QAbstractButton

# ==================================================================================
from ...components import iComponentBase
from .__commandBarButton import iCommandBarButton


# ==================================================================================
class iCommandBarGroup(iComponentBase):
    def __init__(self, name: str, *args, **kwargs) -> None: ...
    def AddButton(self, button: QAbstractButton | iCommandBarButton) -> QAbstractButton | iCommandBarButton: ...
    def RemoveButton(self, button: QAbstractButton | iCommandBarButton) -> None: ...    
    def Contains(self, button: QAbstractButton | iCommandBarButton) -> bool: ...
    def Clear(self) -> None: ...