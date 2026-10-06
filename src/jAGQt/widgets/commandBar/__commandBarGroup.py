# ==================================================================================
# src/jAGQt/widgets/workspace/components/__commandBarGroup.py
# ==================================================================================
from typing import List

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractButton, QWidget

from jAGFx.workflow import workflow

# ==================================================================================
from jAGQt.widgets.components import ComponentBase

from .__commandBar import CommandBar
from .__commandBarButton import CommandBarItem


# ==================================================================================
@workflow("InitializeUI")
class CommandBarGroup(QWidget, ComponentBase):
    OBJECT_NAME = "C_COMMANDBAR_GROUP"
    def __init__(
        self, name: str,
        *args, **kwargs,
    ) -> None:
        super().__init__(objectName=self.OBJECT_NAME, *args, **kwargs)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._buttons: List[QAbstractButton] = List[QAbstractButton]()   
        self._name: str = name

    def _assertIsButton(self, button: QAbstractButton) -> None:
        if not isinstance(button, QAbstractButton | CommandBarItem):
            raise TypeError("AddButton expects a QAbstractButton subclass or a CommandBarItem.")

    # ==================================================================================
    def AddButton(self, button: QAbstractButton) -> QAbstractButton:
        self._assertIsButton(button)
        self.Layout.addWidget(button)
        self._buttons.append(button)
        return button

    def RemoveButton(self, button: QAbstractButton) -> None:
        if not self.Contains(button): return
        self._buttons.remove(button)
        self.Layout.removeWidget(button)
        button.setParent(None)
        button.deleteLater()

    def Clear(self) -> None:
        while self.Layout.count():
            lItem = self.Layout.takeAt(0)
            if lItem is None: continue
            lWidget = lItem.widget()
            if lWidget is not None:
                lWidget.setParent(None)
                lWidget.deleteLater()
        self._buttons.clear()

    def Contains(self, button: QAbstractButton) -> bool:
        return button in self._buttons
        
    @property
    def Count(self) -> int:
        return len(self._buttons)
