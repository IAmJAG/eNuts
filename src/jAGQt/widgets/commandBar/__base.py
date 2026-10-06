# ==================================================================================
# src/jAGQt/widgets/commandBar/__base.py
# ==================================================================================
from typing import Dict

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractButton,
    QBoxLayout,
    QHBoxLayout,
    QSizePolicy,
    QWidget,
)

# ==================================================================================
from ...types.interface.widgets.commandBar import iCommandBarButton
from ...utilities import newLayout
from ..commandBar import commandBarButton
from ..components import ComponentBase

# ==================================================================================
QtPolicy = QSizePolicy.Policy
# ==================================================================================

# ==================================================================================
class _commandBarBase(ComponentBase):
    def _wIntializeUI(self: QWidget) -> None:
        self.Layout = newLayout(QHBoxLayout, spacing=0, margins=(0, 0, 0, 0))
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._buttons: Dict[str, iCommandBarButton]

    # ==================================================================================
    def _assertIsButton(self, button: iCommandBarButton) -> None:
        if not isinstance(button, iCommandBarButton):
            raise TypeError(
                "addButton expects a QAbstractButton subclass or a CommandBarButton."
            )

    # ==================================================================================
    def addButton(self, button: str | iCommandBarButton) -> iCommandBarButton: 
        if isinstance(button, str):
            button: iCommandBarButton = commandBarButton(caption=button)

        layout: QBoxLayout = self.Layout
        layout.addWidget(button)
        self._buttons.update(button)
        return button

    # ==================================================================================
    def removeButton(self, button: str | iCommandBarButton) -> None:
        if not self.contains(button): return
        if isinstance(button, str):
            button: iCommandBarButton = self._buttons.pop(button, None)

        btn: QAbstractButton = button
        layout: QBoxLayout = self.Layout
        if bool(button): layout.removeWidget(button)
        btn.setParent(None)
        btn.deleteLater()

    # ==================================================================================
    def clear(self) -> None:
        layout: QBoxLayout = self.Layout
        while layout.count():
            lItem = layout.takeAt(0)
            if lItem is None: continue
            lWidget = lItem.widget()
            if lWidget is not None:
                lWidget.setParent(None)
                lWidget.deleteLater()

        self._buttons.clear()

    # ==================================================================================
    def contains(self, button: str | iCommandBarButton) -> bool:        
        if isinstance(button, str): 
            return button in self._buttons.keys()
        return button in self._buttons.values()
