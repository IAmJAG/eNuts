# ==================================================================================
# src/jAGQt/types/interface/widgets/__page.py
# ==================================================================================
from typing import Optional
from uuid import UUID

# ==================================================================================
from PySide6.QtWidgets import QAbstractButton, QSizePolicy, QSpacerItem, QWidget

# ==================================================================================
from ..components import iComponentBase
from .__commandBar import iCommandBar

Policy = QSizePolicy.Policy


# ==================================================================================
class Page(QWidget, iComponentBase):
    def __init__(
            self, title: str = "jAGQt Page", description: str = "", 
            commandBarOn: bool = False, id: Optional[str] = None,
            *args, **kwargs
        ) -> None: ...
    
    def addComponent(self, component: iComponentBase) -> None: ...    
    def addWidget(self, widget: QWidget) -> None: ...
    def addSpacer(self, w: int = 0, h: int = 0, hData: Policy = Policy.Expanding, vData: Policy = Policy.Expanding) -> QSpacerItem: ...
    def addCommand(self, button: QAbstractButton, group: Optional[str | CommandBarGroup] = None) -> None: ...
    def addCommandGroup(self, name: str = "", spacing: int = 4): ...

    def setCommandBarState(self, value: bool) -> None: ...

    @property
    def Id(self) -> str | UUID: ...
    @Id.setter
    def Id(self, value: str | UUID) -> str | UUID: ...
    @property
    def Title(self) -> str: ...
    @property
    def Description(self) -> str: ...
    @property
    def CommandBarState(self) -> bool: ...
    