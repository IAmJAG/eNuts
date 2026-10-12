# ==================================================================================
from typing import Dict, Optional, Union
from uuid import UUID

# ==================================================================================
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QBoxLayout, QSizePolicy, QStackedWidget, QWidget

# ==================================================================================
from jAGFx.workflow import workflow
from jAGQt.utilities import newLayout
from jAGQt.widgets.components import ComponentBase
from jAGQt.widgets.page import Page
from jAGQt.widgets.sideBar import SideBar, SideBarItem

# ==================================================================================
QPolicy = QSizePolicy.Policy
# ==================================================================================


# ==================================================================================
@workflow
class Workspace(QWidget, ComponentBase):
    OBJECT_NAME: str = "W_WORKSPACE"
    CurrentPageChanged = Signal(object)

    def __init__(self, title: str = "jAG Workspace", *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        OBJNAME: str = kwargs.pop("objectName", self.OBJECT_NAME)
        self.setObjectName(OBJNAME)
        self.setSizePolicy(QPolicy.Expanding, QPolicy.Expanding)

        self._pageIdMap: Dict[str, Page] = dict[str, Page]()
        self._title: str = title

    def _wInitializeUI(self) -> None:
        title: str = self._title
        del self._title

        sidebar: SideBar = SideBar(title)
        pages: QStackedWidget = QStackedWidget(self)
        pages.setSizePolicy(QPolicy.Expanding, QPolicy.Expanding)
        mainLayout: QBoxLayout = newLayout(QBoxLayout, spacing=0, margins=0)
        mainLayout.setDirection(QBoxLayout.Direction.LeftToRight)
        mainLayout.addWidget(sidebar)
        mainLayout.addWidget(pages, 1)
        self.setLayout(mainLayout)

        self._pages: QStackedWidget = pages
        self._sideBar: SideBar = sidebar
        self._layout: QBoxLayout = mainLayout

        sidebar.ItemClicked.connect(self._onSideBarItemClicked)

    # ==================================================================================
    @property
    def SideBar(self) -> SideBar:
        return self._sideBar

    def addPage(self, page: Page, name: Optional[str] = None) -> None:
        lPageId = str(name) if name is not None else str(page.Id)
        if lPageId in self._pageIdMap:
            return

        page.setSizePolicy(QPolicy.Expanding, QPolicy.Expanding)
        self._pages.addWidget(page)
        self._pageIdMap[lPageId] = page

    def removePage(self, pageId: Union[str, UUID]) -> None:
        pageId = str(pageId) if isinstance(pageId, UUID) else pageId
        if pageId not in self._pageIdMap:
            return
        lPage = self._pageIdMap.pop(pageId)
        self._pages.removeWidget(lPage)

    def setCurrentPage(self, pageId: Union[str, UUID]) -> None:
        pageId = str(pageId) if isinstance(pageId, UUID) else pageId
        if pageId not in self._pageIdMap:
            return
        lPage = self._pageIdMap[pageId]
        self._pages.setCurrentWidget(lPage)
        self.CurrentPageChanged.emit(lPage)

    def hasPage(self, pageId: Union[str, UUID]) -> bool:
        return str(pageId) in self._pageIdMap

    # ==================================================================================
    def _onSideBarItemClicked(self, item: SideBarItem) -> None:
        lId = str(item.id) if item is not None else ""
        if not lId:
            return
        if lId in self._pageIdMap:
            self.setCurrentPage(lId)
