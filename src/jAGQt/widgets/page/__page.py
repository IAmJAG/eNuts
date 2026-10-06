# ==================================================================================
# src/jAGQt/widgets/workspace/__page.py
# ==================================================================================
from typing import Optional, Union
from uuid import UUID, uuid4

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractButton,
    QBoxLayout,
    QSizePolicy,
    QSpacerItem,
    QWidget,
)

from jAGFx.workflow import workflow

# ==================================================================================
from ...components import CommandBarGroup

# ==================================================================================
from ...types.interface.components import iComponentBase
from ...utilities import newLayout
from ...widgets.components import ComponentBase
from .. import Header
from ..components import ComponentBase
from ..workspace.__commandBar import CommandBar


# ==================================================================================
@workflow("InitializeUI")
class Page(QWidget, ComponentBase):
    OBJECT_NAME = "W_PAGE"
    def __init__(
        self, title: str = "jAGQt Page", description: str = "", 
        commandBarOn: bool = False, id: Optional[str] = None,
        *args, **kwargs
    ) -> None: 
        super().__init__(*args, **kwargs)
        self._title = title
        self._description = description    
        self._id: str = str(uuid4()) if id is None else id
        self._commandBar: CommandBar =  commandBarOn

    def _wInitializePage(self):
        # clean up init
        titleText: str = self._title
        descriptionText: str = self._description
        del self._title
        del self._description

        objName: str = self.OBJECT_NAME

        self.setObjectName(objName)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        pageHeader: Header = Header(title=titleText, description=descriptionText)
        pageHeader.setObjectName(f"{objName}_HEADER")

        content: QWidget = QWidget(self)
        content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        content.setObjectName(f"{objName}_CONTENT")

        cntLayout: QBoxLayout = newLayout(QBoxLayout, spacing=0, margins=(0, 0, 0, 0))
        content.setLayout(cntLayout)

        mainLayout: QBoxLayout = newLayout(QBoxLayout, spacing=0, margins=(0, 0, 0, 0), direction=QBoxLayout.Direction.TopToBottom)
        mainLayout.addWidget(pageHeader)
        mainLayout.addWidget(content)
        if self._hasCommandBar:
            self._commandBar = CommandBar()
            cntLayout.addWidget(self._commandBar)

        self._header: Header = pageHeader        
        self._content: QWidget = content

        self.setLayout(mainLayout)
        self._layout: QBoxLayout = cntLayout

    def addComponent(self, component: iComponentBase) -> None:
        self.Layout.addWidget(component)

    def addWidget(self, widget: QWidget) -> None:
        self.Layout.addWidget(widget)

    def addSpacer(
        self, w: int = 0, h: int = 0, 
        hData: QSizePolicy.Policy = QSizePolicy.Policy.Expanding, 
        vData: QSizePolicy.Policy = QSizePolicy.Policy.Expanding
    ) -> QSpacerItem:        
        spacer: QSpacerItem = QSpacerItem(w, h, hData, vData)
        self.Layout.addWidget(spacer)
        return spacer

    def _assertCommandBar(self) -> bool:
        if not hasattr(self, "_commandBar") or self._commandBar is None: 
            warning("CommandBar not initialized")
            return False
        
        return True
    
    def addCommand(self, button: QAbstractButton, group: Optional[str | CommandBarGroup] = None) -> None:
        if self._assertCommandBar(): return
        self._commandBar.AddButton(button, group)

    def addCommandGroup(self, name: str = "", spacing: int = 4):
        if self._assertCommandBar(): return
        self._commandBar.AddGroup(name, spacing)

    # ==================================================================================    
    def _assertWarnHeader(self) -> bool:
        if not hasattr(self, "_header") or self._header is None: 
            warning("Header not initialized")
            return False
        return True

    # ==================================================================================    
    @property
    def Id(self) -> str | UUID:
        return self._id

    @Id.setter
    def Id(self, value: str | UUID) -> str | UUID:
        self._id: str | UUID = value

    @property
    def Title(self) -> str:
        if not self._assertWarnHeader(): return ""
        return self._header.Title

    @Title.setter
    def Title(self, value: str) -> None:
        if not self._assertWarnHeader(): return
        self._header.Title = value

    @property
    def Description(self) -> str:
        if not self._assertWarnHeader(): return ""
        return self._header.Description

    @Description.setter
    def Description(self, value: str) -> None:
        if not self._assertWarnHeader(): return
        self._header.Description = value

    @property
    def CommandBarState(self) -> bool:
        return bool(self._commandBar)

    def setCommandBarState(self, value: bool) -> None:
        if bool(self._commandBar) != value:
            if value:
                self._commandBar = CommandBar()
                self.Layout.addWidget(self._commandBar)

            else:
                self.Layout.removeWidget(self._commandBar)
                self._commandBar.deleteLater()
                self._commandBar = None

            

