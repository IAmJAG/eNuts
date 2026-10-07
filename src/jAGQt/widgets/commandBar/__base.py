# ==================================================================================
from typing import List

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractButton,
    QBoxLayout,
    QSizePolicy,
    QWidget,
)

# ==================================================================================
from ...types.interface.widgets.commandBar import iCommandBarButton
from ...utilities import newLayout

# ==================================================================================
QtPolicy = QSizePolicy.Policy
# ==================================================================================

# ==================================================================================
class _commandBarBase:
    def _wInitializeShell(self: QWidget) -> None:
        self.Layout = newLayout(QBoxLayout, spacing=0, margins=(0, 0, 0, 0))
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._buttons: List[iCommandBarButton] = list[iCommandBarButton]()        

    # ==================================================================================
    def _assertIsButton(self: QWidget, button: iCommandBarButton) -> None:
        if not isinstance(button, iCommandBarButton):
            raise TypeError(
                "addButton expects a QAbstractButton subclass or a CommandBarButton."
            )

    # ==================================================================================
    def addButton(self: QWidget, button: iCommandBarButton) -> iCommandBarButton: 
        layout: QBoxLayout = self.Layout
        layout.addWidget(button)
        self._buttons.append(button)
        return button

    # ==================================================================================
    def removeButton(self, button: str | iCommandBarButton) -> None:
        if not self.contains(button): return
        if isinstance(button, str):
            for btn in self._buttons:
                if btn.text() == button:
                    button: iCommandBarButton = btn

            btnIdx: int = self._buttons.index(button)
            button: iCommandBarButton = self._buttons.pop(btnIdx)

        btn: QAbstractButton = button
        layout: QBoxLayout = self.Layout
        if btn: layout.removeWidget(btn)
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
    def contains(self, button: iCommandBarButton) -> bool:
        return button in self._buttons
