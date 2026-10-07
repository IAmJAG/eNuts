# ==================================================================================
# src/jAGQt/widgets/commandBar/__commandBar.py
# ==================================================================================
from typing import Dict, Optional, Type, Union

# ==================================================================================
from PySide6.QtWidgets import QAbstractButton, QBoxLayout, QSizePolicy, QWidget

# ==================================================================================
from jAGFx.workflow import workflow

# ==================================================================================
from ...types.interface.widgets.commandBar import iCommandBarButton as ICBB
from ...types.interface.widgets.commandBar import iCommandBarGroup as ICBG
from ...utilities import newLayout
from ..components import ComponentBase
from .__base import _commandBarBase
from .__commandBarGroup import CommandBarGroup
from .commandBarButton import CommandBarButton

# ==================================================================================
QtPolicy = QSizePolicy.Policy
# ==================================================================================

# ==================================================================================
@workflow("InitializeUI")
class CommandBar(QWidget, ComponentBase, _commandBarBase):
    OBJECT_NAME = "W_COMMANDBAR"
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._groups: Dict[str, ICBG] = dict[str, ICBG]()
        self._buttons: list[ICBB] = list[ICBB]()

    def _wInitializeUI(self) -> None:
        super()._wInitializeShell()
        self.setObjectName(self.OBJECT_NAME)
        self.setSizePolicy(QtPolicy.Expanding, QtPolicy.Fixed)
        self.Layout = newLayout(QBoxLayout, spacing=0, margins=(0, 0, 0, 0))

    def _assertButton(self, button: QAbstractButton) -> None:
        if not isinstance(button, ICBB):
            raise TypeError("CommandBar.AddButton expects a iCommandBarButton contractor")

    def addButton(self, button: str | ICBB, group: str | ICBG = None) -> ICBB:
        if isinstance(button, str): 
            button: ICBB = CommandBarButton(button)

        lGroup: Optional[ICBG] = self._resolveGroup(group)
        if lGroup is None: 
            return super().addButton(button)
        return lGroup.addButton(button)

    def addGroup(self, name: str) -> ICBG:
        if name.strip() == "": 
            warning("addGroup: Group name cannot be empty")
            return None
        
        if name in self._groups:
            return self._groups[name]

        group: ICBG = CommandBarGroup(name)
        self._groups[name] = group
        self.Layout.addWidget(group)
        return group

    def addStretch(self, stretch: int = 1) -> None:
        self.Layout.addStretch(stretch)

    def setSpacingSize(self, size: int) -> None:
        self.Layout.setSpacing(size)

    def clear(self) -> None:
        while self.Layout.count():
            lItem = self.Layout.takeAt(0)
            if lItem is None: continue
            lWidget = lItem.widget()
            if lWidget is not None:
                lWidget.setParent(None)
                lWidget.deleteLater()
        self._groups.clear()

    # ==================================================================================
    def _resolveGroup(self, group: Optional[Union[str, ICBG]]) -> Optional[ICBG]:
        if group is None: return None
        if isinstance(group, ICBG):
            if group not in self._groups.values():                
                self.Layout.addWidget(group)
                self._groups.update({group.Name: group})
            return group

        lExisting = self._groups.get(group)
        if lExisting is not None: return lExisting
        
        return self.addGroup(name=group)
