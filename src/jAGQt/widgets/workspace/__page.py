# ==================================================================================
# src/jAGQt/widgets/workspace/__page.py
# ==================================================================================
from typing import Optional
from uuid import uuid4

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QBoxLayout,
    QFrame,
    QLabel,
    QSizePolicy,
    QWidget,
)

# ==================================================================================
from jAGQt.types.components import ComponentBase
from jAGQt.utilities import newLayout

# ==================================================================================
from .__commandBar import CommandBar


# ==================================================================================
class Page(QWidget, ComponentBase):
    """Single workspace page (title + content + CommandBar).

        Page
        ├── Header (Title / Description)
        ├── Content
        └── CommandBar   ← always present; consumers AddButton only
    """

    def __init__(
        self,
        title: str = "",
        description: str = "",
        parent: Optional[QWidget] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)

        self.setObjectName("Page")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._id: str = str(uuid4())
        self._title: str = title
        self._description: str = description
        self._content: Optional[QWidget] = None
        self._commandBar: Optional[CommandBar] = None

        self.Layout = newLayout(QBoxLayout, spacing=8, margins=(16, 16, 16, 16))

        self._titleLabel = QLabel(title, self)
        self._titleLabel.setObjectName("PAGE_TITLE")
        self.Layout.addWidget(self._titleLabel)

        self._descriptionLabel = QLabel(description, self)
        self._descriptionLabel.setObjectName("PAGE_DESCRIPTION")
        self._descriptionLabel.setVisible(bool(description))
        self.Layout.addWidget(self._descriptionLabel)

        self.Content = None
        self.CommandBar = CommandBar(parent=self)

    # ==================================================================================
    @property
    def Id(self) -> str:
        """Immutable identifier used as the key in Workspace."""
        return self._id

    @property
    def id(self) -> str:
        return self._id

    @property
    def Title(self) -> str:
        return self._title

    @Title.setter
    def Title(self, value: str) -> None:
        self._title = value
        self._titleLabel.setText(value)

    @property
    def Description(self) -> str:
        return self._description

    @Description.setter
    def Description(self, value: str) -> None:
        self._description = value
        self._descriptionLabel.setText(value)
        self._descriptionLabel.setVisible(bool(value))

    @property
    def Content(self) -> Optional[QWidget]:
        return self._content

    @Content.setter
    def Content(self, value: Optional[QWidget]) -> None:
        if self._content is not None:
            self.Layout.removeWidget(self._content)
            self._content.hide()
            self._content.deleteLater()
            self._content = None

        if value is None:
            value = QFrame(self)
            value.setObjectName("PageContent")
            lCntLayout = newLayout(QBoxLayout, spacing=2, margins=(7, 7, 7, 7))
            value.setLayout(lCntLayout)
            lCntLayout.addStretch()

        self._content = value
        value.setParent(self)

        lInsertIndex = self.Layout.count()
        if self._commandBar is not None:
            lInsertIndex = self.Layout.indexOf(self._commandBar)
        self.Layout.insertWidget(lInsertIndex, value, 1)

    @property
    def CommandBar(self) -> Optional[CommandBar]:
        return self._commandBar

    @CommandBar.setter
    def CommandBar(self, value: Optional[CommandBar]) -> None:
        if self._commandBar is not None:
            self.Layout.removeWidget(self._commandBar)
            self._commandBar.hide()
            self._commandBar.deleteLater()
            self._commandBar = None

        if value is not None:
            self._commandBar = value
            value.setParent(self)
            self.Layout.addWidget(value)

    content = Content
    commandBar = CommandBar
