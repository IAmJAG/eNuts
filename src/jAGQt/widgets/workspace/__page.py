# ==================================================================================
from uuid import UUID, uuid4

# ==================================================================================
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

# ==================================================================================
from ...types.components import ComponentBase


# ==================================================================================
class Page(QWidget, ComponentBase):
    def __init__(self, title: str, description: str = "", parent=None) -> None:
        super().__init__(parent)
        self._id: UUID = str(uuid4())
        self._title: str = title
        self._description: str = description
        self._content: QWidget  = None

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 16, 16, 16)
        self._layout.setSpacing(8)

        titleWidget = QLabel(title)
        titleWidget.setObjectName("PAGE_TITLE")
        self._layout.addWidget(titleWidget)

        self.content = None
        self.commandBar = None

    @property
    def title(self) -> str:
        return self._title

    @property
    def content(self) -> QWidget:
        return self._content

    @content.setter
    def content(self, value: QFrame | None) -> None:
        if hasattr(self, "_content"):
            self.Layout.removeWidget(self._content)
            self._content.setParent(None)
            self._content.deleteLater()

        if value is None:
            value: QFrame = QFrame()
            cntLayout: QVBoxLayout = QVBoxLayout(value)
            cntLayout.setContentsMargins(7, 7, 7, 7)
            cntLayout.setSpacing(2)
            cntLayout.addStretch()

        self._content = value
        value.setParent(self)

        self.Layout.addWidget(value, 1)

    @property
    def commandBar(self) -> CommandBar | None:
        return self._commandBar

    @commandBar.setter
    def commandBar(self, value: CommandBar | None) -> None:
        if not hasattr(self, "_commandBar"):
            self._commandBar = None

        if self._commandBar is not None:
            self.Layout.removeWidget(self._commandBar)
            self._commandBar.setParent(None)
            self._commandBar.deleteLater()
            self._commandBar = None

        if value is not None:
            self._commandBar = value
            value.setParent(self)
            self.Layout.addWidget(value)
