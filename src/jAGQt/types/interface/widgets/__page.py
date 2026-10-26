# ==================================================================================
# src/jAGQt/types/interface/widgets/__page.py
# ==================================================================================
from typing import Optional, Union
from uuid import UUID

# ==================================================================================
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QAbstractButton, QSizePolicy, QSpacerItem, QWidget

# ==================================================================================
from ..components import iComponentBase
from .__commandBar import iCommandBar

Policy = QSizePolicy.Policy


# ==================================================================================
class Page(QWidget, iComponentBase):
    def __init__(
            self,
            title: str = "jAGQt Page",
            description: str = "",
            icon: Optional[Union[QIcon, QPixmap, str]] = None,
            commandBarOn: bool = False,
            id: Optional[str] = None,
            *args,
            **kwargs
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
    @Title.setter
    def Title(self, value: str) -> None: ...
    @property
    def Description(self) -> str: ...
    @Description.setter
    def Description(self, value: str) -> None: ...
    @property
    def Icon(self) -> Optional[Union[QIcon, QPixmap]]: ...
    @Icon.setter
    def Icon(self, value: Optional[Union[QIcon, QPixmap, str]]) -> None: ...
    @property
    def CommandBarState(self) -> bool: ...
    @CommandBarState.setter
    def CommandBarState(self, value: bool) -> None: ...
