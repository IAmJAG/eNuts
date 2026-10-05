# ==================================================================================
# src/jAGQt/widgets/workspace/components/__commandBarGroup.py
# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractButton, QHBoxLayout, QSizePolicy, QWidget

# ==================================================================================
from jAGQt.types.components import ComponentBase
from jAGQt.utilities import newLayout


# ==================================================================================
class CommandBarGroup(QWidget, ComponentBase):
    def __init__(
        self, name: str = "", spacing: int = 4, parent: Optional[QWidget] = None,
        *args, **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)

        self.setObjectName("CommandBarGroup")
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._name: str = name
        self._buttons: list[QAbstractButton] = []
        self.Layout = newLayout(QHBoxLayout, spacing=spacing, margins=(0, 0, 0, 0))

    # ==================================================================================
    def AddButton(self, button: QAbstractButton) -> QAbstractButton:
        if not isinstance(button, QAbstractButton):
            raise TypeError(
                "CommandBarGroup.AddButton expects a QAbstractButton subclass"
            )

        button.setParent(self)        
        self.Layout.addWidget(button)
        self._buttons.append(button)
        return button

    def RemoveButton(self, button: QAbstractButton) -> None:
        if button not in self._buttons: return
        self._buttons.remove(button)
        self.Layout.removeWidget(button)
        button.setParent(None)

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

    # ==================================================================================
    @property
    def Name(self) -> str:
        return self._name

    @Name.setter
    def Name(self, value: str) -> None:
        self._name = value

    @property
    def Buttons(self) -> list[QAbstractButton]:
        return list(self._buttons)

    @property
    def Count(self) -> int:
        return len(self._buttons)
