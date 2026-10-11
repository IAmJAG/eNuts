# ==================================================================================
# src/jAGQt/widgets/workspace/__workspace.py
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
from jAGQt.widgets.sideBar import SideBar

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
        mainLayout.addWidget(pages)
        self.setLayout(mainLayout)

        self._pages: QStackedWidget = pages
        self._layout: QBoxLayout = newLayout(QBoxLayout, spacing=0, margins=0)

    def addPage(self, page: Page, name: Optional[str] = None):
        lPageId = str(page.Id)
        if lPageId in self._pageIdMap: return

        page.setSizePolicy(QPolicy.Expanding, QPolicy.Expanding)
        self._pages.addWidget(page)
        self._pageIdMap[lPageId] = page

    def removePage(self, pageId: Union[str, UUID]):
        pageId: str = str(pageId) if isinstance(pageId, UUID) else pageId
        self._pages.removeWidget(self._pageIdMap[pageId])
        del self._pageIdMap[pageId]

    def setCurrentPage(self, pageId: Union[str, UUID]):
        pageId: str = str(pageId) if isinstance(pageId, UUID) else pageId
        self._pages.setCurrentWidget(self._pageIdMap[pageId])

        
