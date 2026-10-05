# ==================================================================================
from typing import Dict

# ==================================================================================
from PySide6.QtWidgets import QStackedWidget, QWidget

# ==================================================================================
from .__page import Page


# ==================================================================================
class Workspace(QWidget):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self._stack: QStackedWidget = QStackedWidget(self)
        self._pages: Dict[str, Page] = {}

    def addPage(self, page: Page) -> None:
        self._stack.addWidget(page)
        self._pages[page.id] = page

    def setCurrentPage(self, key: str) -> None:
        self._stack.setCurrentWidget(self._pages[key])
