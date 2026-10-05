# ==================================================================================
# src/jAGQt/widgets/workspace/__commandBar.py
# ==================================================================================
from typing import Optional, Union

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractButton, QBoxLayout, QSizePolicy, QWidget

# ==================================================================================
from jAGQt.types.components import ComponentBase
from jAGQt.utilities import newLayout

# ==================================================================================
from .components import CommandBarGroup


# ==================================================================================
class CommandBar(QWidget, ComponentBase):
    """Bottom command / action bar for a Page (SideBar-style composer)."""

    def __init__(
        self, spacing: int = 6, parent: Optional[QWidget] = None,
        *args, **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)

        self.setObjectName("CommandBar")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._groups: dict[str, CommandBarGroup] = {}
        self.Layout = newLayout(QBoxLayout, spacing=spacing, margins=(8, 4, 8, 4))

    # ==================================================================================
    def AddButton(
        self, button: QAbstractButton, group: Optional[Union[str, CommandBarGroup]] = None,
    ) -> QAbstractButton:
        if not isinstance(button, QAbstractButton):
            raise TypeError("CommandBar.AddButton expects a QAbstractButton subclass")

        if group is None:
            button.setParent(self)
            self.Layout.addWidget(button)
            return button

        lGroup = self._resolveGroup(group)
        return lGroup.AddButton(button)

    def AddGroup(self, name: str = "", spacing: int = 4) -> CommandBarGroup:
        if name and name in self._groups:
            return self._groups[name]

        lGroup = CommandBarGroup(name=name, spacing=spacing, parent=self)
        self.Layout.addWidget(lGroup)
        if name:
            self._groups[name] = lGroup
        return lGroup

    def AddStretch(self, stretch: int = 1) -> None:
        self.Layout.addStretch(stretch)

    def AddSpacing(self, size: int) -> None:
        self.Layout.addSpacing(size)

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
                group.setParent(self)
                self.Layout.addWidget(group)
                if group.Name:
                    self._groups[group.Name] = group
            return group

        lExisting = self._groups.get(group)
        if lExisting is not None:
            return lExisting
        return self.AddGroup(name=group)
