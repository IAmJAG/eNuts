# ==================================================================================
from typing import List, Optional

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
    def _wInitializeBase(self: QWidget) -> None:
        self.Layout = newLayout(
            QBoxLayout,
            spacing=0,
            margins=(0, 0, 0, 0),
            direction=QBoxLayout.Direction.LeftToRight,
        )
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
        if isinstance(button, str):
            button = next((b for b in self._buttons if b.text() == button), None)

        if button not in self._buttons:
            return

        self._buttons.remove(button)
        self.Layout.removeWidget(button)
        button.setParent(None)
        button.deleteLater()

    # ==================================================================================
    def clear(self) -> None:
        layout: QBoxLayout = self.Layout
        while layout.count():
            lItem = layout.takeAt(0)
            if lItem is None:
                continue
            lWidget = lItem.widget()
            if lWidget is not None:
                lWidget.setParent(None)
                lWidget.deleteLater()

        self._buttons.clear()

    # ==================================================================================
    def contains(self, button: str | iCommandBarButton) -> bool:
        if isinstance(button, str):
            return any(b.text() == button for b in self._buttons)
        return button in self._buttons
