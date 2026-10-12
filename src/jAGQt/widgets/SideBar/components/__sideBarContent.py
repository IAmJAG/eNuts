# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QBoxLayout, QFrame, QScrollArea, QSizePolicy, QWidget

# ==================================================================================
from jAGFx.workflow import workflow

# ==================================================================================
from ....utilities import newLayout
from ...components import ComponentBase

# ==================================================================================
QPolicy = QSizePolicy.Policy
# ==================================================================================


# ==================================================================================
@workflow
class SideBarContent(QScrollArea, ComponentBase):
    OBJECT_NAME = "W_SIDEBAR_CONTENT"
    CONTAINER_NAME = "W_SIDEBAR_CONTENT_CONTAINER"

    def __init__(
        self, spacing: int = 2, margins: tuple[int, int, int, int] = (0, 0, 0, 0),
        *args, **kwargs
    ) -> None:
        OBJNAME = kwargs.pop("objectName", self.OBJECT_NAME)
        super().__init__(objectName=OBJNAME, *args, **kwargs)
        self._spacing = int(spacing)
        self._margins = margins

    def _wInitializeUI(self) -> None:
        spacing = self._spacing
        margins = self._margins

        del self._spacing
        del self._margins

        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setSizePolicy(QPolicy.Expanding, QPolicy.Expanding)

        self._container = QWidget()
        self._container.setObjectName(self.CONTAINER_NAME)

        layout: QBoxLayout = newLayout(
            QBoxLayout,
            spacing=spacing,
            margins=margins,
            direction=QBoxLayout.Direction.TopToBottom,
        )
        
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._container.setLayout(layout)
        self.setWidget(self._container)
        self._layout = layout

    def addWidget(self, widget: QWidget, stretch: int = 0) -> None:
        self._layout.addWidget(widget, stretch)

    def insertWidget(self, index: int, widget: QWidget, stretch: int = 0) -> None:
        self._layout.insertWidget(index, widget, stretch)

    def removeWidget(self, widget: QWidget, delete: bool = True) -> None:
        self._layout.removeWidget(widget)
        widget.setParent(None)
        if delete:
            widget.deleteLater()

    def clear(self, delete: bool = True) -> None:
        while self._layout.count():
            item = self._layout.takeAt(0)
            w = item.widget()
            if w is None: continue
            w.setParent(None)
            if delete: w.deleteLater()

    def addStretch(self, stretch: int = 1) -> None:
        self._layout.addStretch(stretch)

    def count(self) -> int:
        return self._layout.count()
