# ==================================================================================
# src/jAGQt/widgets/workspace/__commandBar.py
# ==================================================================================
from typing import Optional, Union

# ==================================================================================
from PySide6.QtWidgets import QAbstractButton

# ==================================================================================
from ...components import iComponentBase
from .__commandBarButton import iCommandBarItem
from .__commandBarGroup import iCommandBarGroup


# ==================================================================================
class iCommandBar(iComponentBase):
    def AddButton(self, button: QAbstractButton | iCommandBarItem, group: Optional[Union[str, iCommandBarGroup]] = None) -> QAbstractButton | iCommandBarItem: ...
    def AddGroup(self, name: str) -> iCommandBarGroup: ...
    def AddStretch(self, stretch: int = 1) -> None: ...
    def setSpacingSize(self, size: int) -> None: ...
    def Clear(self) -> None: ...