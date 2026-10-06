# ==================================================================================
# src/jAGQt/widgets/workspace/__commandBar.py
# ==================================================================================
from typing import Dict, Optional, Union, overload

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractButton, QBoxLayout, QSizePolicy, QWidget

from jAGFx.workflow import workflow
from jAGQt.utilities import newLayout

# ==================================================================================
from jAGQt.widgets.components import ComponentBase

# ==================================================================================
from ...types.interface.widgets.commandBar import (
    iCommandBar,
    iCommandBarButton,
    iCommandBarGroup,
)
from .__base import _commandBarBase
from .__commandBarGroup import CommandBarGroup

# ==================================================================================
QtPolicy = QSizePolicy.Policy
# ==================================================================================


# ==================================================================================
@workflow("InitializeUI")
class CommandBar(QWidget, ComponentBase, _commandBarBase):
    OBJECT_NAME = "W_COMMANDBAR"
    def __init__(self, *args, **kwargs,) -> None:
        super().__init__(*args, **kwargs)
        self._groups: Dict[str, iCommandBarGroup] = dict[str, iCommandBarGroup]()        
        self._buttons: Dict[str, iCommandBarButton] = dict[str, iCommandBarButton]()

    def _wIntializeUI(self) -> None:
        super()._wIntializeUI()
        self.setObjectName("CommandBar")
        self.setSizePolicy(QtPolicy.Expanding, QtPolicy.Fixed)
        self.Layout = newLayout(QBoxLayout, spacing=0, margins=(0, 0, 0, 0))

    def _assertButton(self, button: QAbstractButton) -> None:
        if not isinstance(button, QAbstractButton | iCommandBarButton):
            raise TypeError("CommandBar.AddButton expects a QAbstractButton subclass")

    def addButton(
        self,
        button: str | iCommandBarButton,
        group: Optional[Union[str, iCommandBarGroup]] = None,
    ) -> iCommandBarButton:        
        
        group: CommandBarGroup = self._resolveGroup(group)
        if group is None:
            return super().addButton(button)                
        return group.addButton(button)

    def addGroup(self, name: str) -> CommandBarGroup:
        if name in self._groups: 
            return self._groups[name]
        
        lGroup = CommandBarGroup(name)        
        self._groups[name] = lGroup
        self.Layout.addWidget(lGroup)
        return lGroup

    def addStretch(self, stretch: int = 1) -> None:
        self.Layout.addStretch(stretch)

    def setSpacingSize(self, size: int) -> None:
        self.Layout.setSpacing(size)

    def clear(self) -> None:
        while self.Layout.count():
            lItem = self.Layout.takeAt(0)
            if lItem is None:
                continue
            lWidget = lItem.widget()
            if lWidget is not None:
                lWidget.setParent(None)
                lWidget.deleteLater()
        self._groups.clear()

    # ==================================================================================
    def _resolveGroup(self, group: Union[str, CommandBarGroup]) -> CommandBarGroup:
        if isinstance(group, CommandBarGroup):
            if group not in self._groups.values():
                self.Layout.addWidget(group)
                self._groups[group.Name] = group                
            return group

        lExisting = self._groups.get(group)
        if lExisting is not None: return lExisting
        return self.addGroup(name=group)
