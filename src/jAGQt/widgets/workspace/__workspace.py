# ==================================================================================
# src/jAGQt/widgets/workspace/__workspace.py
# ==================================================================================
from typing import Dict, Optional, Union
from uuid import UUID

# ==================================================================================
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QBoxLayout, QSizePolicy, QStackedWidget, QWidget

from jAGQt.utilities import newLayout

# ==================================================================================
from jAGQt.widgets.components import ComponentBase
from jAGQt.widgets.sideBar.components import SideBarItem

# ==================================================================================
from ..page.__page import Page


# ==================================================================================
def _asId(value: Union[str, UUID]) -> str:
    return str(value)


# ==================================================================================
class Workspace(QWidget, ComponentBase):
    """Manages Pages and the SideBarItem.Id → Page.Id navigation map."""

    CurrentPageChanged = Signal(object)  # emits Page | None

    def __init__(self, parent: Optional[QWidget] = None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        self.setObjectName("Workspace")
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        self._stack: QStackedWidget = QStackedWidget(self)
        self._stack.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self._pages: Dict[str, Page] = {}
        self._nameToId: Dict[str, str] = {}
        self._itemToPage: Dict[str, str] = {}

        self._layout: QBoxLayout = newLayout(QBoxLayout, spacing=0, margins=0)
        self.Layout.addWidget(self._stack, 1)  # stretch — fill host

        self._stack.currentChanged.connect(self._onStackChanged)

    # ==================================================================================
    def AddPage(self, page: Page, name: Optional[str] = None) -> None:
        lPageId = _asId(page.Id)
        if lPageId in self._pages:
            return

        page.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self._stack.addWidget(page)
        self._pages[lPageId] = page
        lKey = name if name is not None else page.Title
        if lKey:
            self._nameToId[lKey] = lPageId

    def Link(self, item: SideBarItem, page: Page) -> None:
        """Bridge SideBarItem.Id → Page.Id. Workspace owns the mapping."""
        self._itemToPage[_asId(item.Id)] = _asId(page.Id)
        if _asId(page.Id) not in self._pages:
            self.AddPage(page)

    def Unlink(self, item: SideBarItem) -> None:
        self._itemToPage.pop(_asId(item.Id), None)

    def NavigateByItem(self, item: SideBarItem) -> bool:
        """Resolve item → page and switch. Returns True if navigated."""
        lPageId = self._itemToPage.get(_asId(item.Id))
        if lPageId is None:
            return False
        lPage = self._pages.get(lPageId)
        if lPage is None:
            return False
        self._stack.setCurrentWidget(lPage)
        return True

    def SetCurrentPage(self, key: str) -> None:
        """Switch by page Id or registered name."""
        lId = self._nameToId.get(key, key)
        lPage = self._pages.get(lId)
        if lPage is not None:
            self._stack.setCurrentWidget(lPage)

    def GetPage(self, key: str) -> Optional[Page]:
        lId = self._nameToId.get(key, key)
        return self._pages.get(lId)

    def GetPageForItem(self, item: SideBarItem) -> Optional[Page]:
        lPageId = self._itemToPage.get(_asId(item.Id))
        return self._pages.get(lPageId) if lPageId else None

    def RemovePage(self, key: str) -> None:
        """Remove by Id or by registered name."""
        lId = self._nameToId.pop(key, key)
        lPage = self._pages.pop(lId, None)
        if lPage is None:
            return
        for lName, lMappedId in list(self._nameToId.items()):
            if lMappedId == lId:
                del self._nameToId[lName]
        for lItemId, lPageId in list(self._itemToPage.items()):
            if lPageId == lId:
                del self._itemToPage[lItemId]
        self._stack.removeWidget(lPage)
        lPage.hide()
        lPage.deleteLater()

    def Clear(self) -> None:
        self._itemToPage.clear()
        for lKey in list(self._pages.keys()):
            self.RemovePage(lKey)

    addPage = AddPage
    setCurrentPage = SetCurrentPage

    # ==================================================================================
    @property
    def CurrentPage(self) -> Optional[Page]:
        lWidget = self._stack.currentWidget()
        return lWidget if isinstance(lWidget, Page) else None

    @property
    def Pages(self) -> Dict[str, Page]:
        return dict(self._pages)

    @property
    def Count(self) -> int:
        return len(self._pages)

    # ==================================================================================
    def _onStackChanged(self, index: int) -> None:
        lPage = self._stack.widget(index) if index >= 0 else None
        self.CurrentPageChanged.emit(lPage if isinstance(lPage, Page) else None)
