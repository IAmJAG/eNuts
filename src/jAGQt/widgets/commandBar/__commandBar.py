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
    iCommandBarGroup,
    iCommandBarItem,
)
from .__commandBarButton import CommandBarItem
from .__commandBarGroup import CommandBarGroup


# ==================================================================================
@workflow("InitializeUI")
class CommandBar(QWidget, ComponentBase, iCommandBar):
    OBJECT_NAME = "W_COMMANDBAR"
    def __init__(self, *args, **kwargs,) -> None:
        super().__init__(*args, **kwargs)
        self._groups: Dict[str, iCommandBarGroup] = dict[str, iCommandBarGroup]()        

    def _wIntializeUI(self) -> None:
        self.setObjectName("CommandBar")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.Layout = newLayout(QBoxLayout, spacing=0, margins=(0, 0, 0, 0))

    def _assertButton(self, button: QAbstractButton) -> None:
        if not isinstance(button, QAbstractButton | iCommandBarItem):
            raise TypeError("CommandBar.AddButton expects a QAbstractButton subclass")

    def AddButton(
        self,
        button: QAbstractButton | iCommandBarItem,
        group: Optional[Union[str, iCommandBarGroup]] = None,
    ) -> QAbstractButton | iCommandBarItem:        
        if not isinstance(button, QAbstractButton):
            raise TypeError("CommandBar.AddButton expects a QAbstractButton subclass")

        group: CommandBarGroup = self._resolveGroup(group)
        if group is None:
            self.Layout.addWidget(button)
            return button
            
        return group.AddButton(button)

    def AddGroup(self, name: str) -> CommandBarGroup:
        if name in self._groups: 
            return self._groups[name]
        
        lGroup = CommandBarGroup(name)        
        self._groups[name] = lGroup
        self.Layout.addWidget(lGroup)
        return lGroup

    def AddStretch(self, stretch: int = 1) -> None:
        self.Layout.addStretch(stretch)

    def setSpacingSize(self, size: int) -> None:
        self.Layout.setSpacing(size)

    def Clear(self) -> None:
        while self.Layout.count():
            lItem = self.Layout.takeAt(0)
            if lItem is None:
                continue
            lWidget = lItem.widget()
            if lWidget is not None:
                lWidget.setParent(None)
                lWidget.deleteLater()
        self._groups.clear()

    def GetGroup(self, name: str) -> Optional[CommandBarGroup]:
        return self._groups.get(name)

    # ==================================================================================
    def _resolveGroup(self, group: Union[str, CommandBarGroup]) -> CommandBarGroup:
        if isinstance(group, CommandBarGroup):
            if group not in self._groups.values():
                self.Layout.addWidget(group)
                self._groups[group.Name] = group                
            return group

        lExisting = self._groups.get(group)
        if lExisting is not None: return lExisting
        return self.AddGroup(name=group)
