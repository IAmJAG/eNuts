# ==================================================================================
# src/jAGQt/widgets/page/__page.py
# ==================================================================================
from typing import Optional
from uuid import UUID, uuid4

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QBoxLayout,
    QSizePolicy,
    QSpacerItem,
    QWidget,
)

from jAGFx.workflow import workflow

# ==================================================================================
from ...types.interface.components import iComponentBase
from ...types.interface.widgets.commandBar import (
    iCommandBar,
    iCommandBarButton,
    iCommandBarGroup,
)
from ...utilities import newLayout
from .. import Header
from ..commandBar import CommandBar
from ..components import ComponentBase


# ==================================================================================
@workflow("InitializeUI")
class Page(QWidget, ComponentBase):
    OBJECT_NAME = "W_PAGE"

    def __init__(
        self,
        title: str = "jAGQt Page",
        description: str = "",
        commandBarOn: bool = False,
        id: Optional[str] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._id: str = str(uuid4()) if id is None else id

        # temp until _wInitializeUI
        self._title = title
        self._description = description
        self._isCommandBarOn: bool = commandBarOn

    def _wInitializeUI(self) -> None:
        titleText: str = self._title
        descriptionText: str = self._description
        isCommandBarOn: bool = self._isCommandBarOn
        OBJNAME: str = self.OBJECT_NAME

        del self._title
        del self._description
        del self._isCommandBarOn

        self.setObjectName(OBJNAME)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        # parent=self — never create floating children
        pageHeader: Header = Header(
            title=titleText,
            description=descriptionText,
            parent=self,
        )
        pageHeader.setObjectName(f"{OBJNAME}_HEADER")

        content: QWidget = QWidget(self)
        content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        content.setObjectName(f"{OBJNAME}_CONTENT")

        cntLayout: QBoxLayout = newLayout(QBoxLayout, spacing=0, margins=(0, 0, 0, 0))
        content.setLayout(cntLayout)

        commandBar: Optional[iCommandBar] = (
            CommandBar(parent=self) if isCommandBarOn else None
        )

        mainLayout: QBoxLayout = newLayout(
            QBoxLayout,
            spacing=0,
            margins=(0, 0, 0, 0),
            direction=QBoxLayout.Direction.TopToBottom,
        )
        mainLayout.addWidget(pageHeader)
        mainLayout.addWidget(content)
        if commandBar is not None:
            mainLayout.addWidget(commandBar)

        self._header: Header = pageHeader
        self._content: QWidget = content
        self._commandBar: Optional[iCommandBar] = commandBar
        self._mainLayout: QBoxLayout = mainLayout

        self.setLayout(mainLayout)
        # content-area layout used by addWidget / addSpacer
        self._layout: QBoxLayout = cntLayout

    def addComponent(self, component: iComponentBase) -> None:
        self.addWidget(component)

    def addWidget(self, widget: QWidget) -> None:
        self.Layout.addWidget(widget)

    def addSpacer(
        self,
        w: int = 0,
        h: int = 0,
        hData: QSizePolicy.Policy = QSizePolicy.Policy.Expanding,
        vData: QSizePolicy.Policy = QSizePolicy.Policy.Expanding,
    ) -> QSpacerItem:
        spacer: QSpacerItem = QSpacerItem(w, h, hData, vData)
        self.Layout.addSpacerItem(spacer)
        return spacer

    def _assertCommandBar(self) -> bool:
        if self._commandBar is None:
            warning("CommandBar not initialized")
            return False
        return True

    def addCommand(
        self,
        button: str | iCommandBarButton,
        group: Optional[str | iCommandBarGroup] = None,
    ) -> None:
        if not self._assertCommandBar():
            return
        self._commandBar.addButton(button, group)

    def addCommandGroup(self, name: str | iCommandBarGroup) -> None:
        if not self._assertCommandBar():
            return
        self._commandBar.addGroup(name)

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
    def Id(self, value: str | UUID) -> None:
        self._id = value

    @property
    def Title(self) -> str:
        if not self._assertWarnHeader():
            return ""
        return self._header.Title

    @Title.setter
    def Title(self, value: str) -> None:
        if not self._assertWarnHeader():
            return
        self._header.Title = value

    @property
    def Description(self) -> str:
        if not self._assertWarnHeader():
            return ""
        return self._header.Description

    @Description.setter
    def Description(self, value: str) -> None:
        if not self._assertWarnHeader():
            return
        self._header.Description = value

    @property
    def Content(self) -> QWidget:
        return self._content

    @Content.setter
    def Content(self, widget: QWidget) -> None:
        """Replace content-host children with ``widget`` (reparented into the host)."""
        while self._layout.count():
            lItem = self._layout.takeAt(0)
            if lItem is None:
                continue
            lW = lItem.widget()
            if lW is not None:
                lW.setParent(None)
                lW.deleteLater()
        if widget is not None:
            widget.setParent(self._content)
            self._layout.addWidget(widget)

    @property
    def CommandBarState(self) -> bool:
        return bool(self._commandBar)

    def setCommandBarState(self, value: bool) -> None:
        if bool(self._commandBar) == value:
            return
        if value:
            self._commandBar = CommandBar(parent=self)
            self._mainLayout.addWidget(self._commandBar)
        else:
            self._mainLayout.removeWidget(self._commandBar)
            self._commandBar.deleteLater()
            self._commandBar = None
