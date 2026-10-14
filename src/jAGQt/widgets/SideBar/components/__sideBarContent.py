# ==================================================================================
# src/jAGQt/widgets/SideBar/components/__sideBarContent.py
# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QBoxLayout, QFrame, QScrollArea, QSizePolicy, QWidget

from ....utilities import newLayout

# ==================================================================================
from ...components import ComponentBase


# ==================================================================================
class SideBarContent(QScrollArea, ComponentBase):
    """Scrollable content area that holds SideBar items, groups and separators."""

    def __init__(
        self, spacing: int = 2, margins: tuple[int, int, int, int] = (0, 0, 0, 0),
        parent: Optional[QWidget] = None, *args, **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)

        self.setObjectName("SideBarContent")
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._container = QWidget(self)
        self._container.setObjectName("SideBarContentContainer")
        self._layout: QBoxLayout = newLayout(QBoxLayout, spacing=spacing, margins=margins)
        self._layout.setDirection(QBoxLayout.Direction.TopToBottom)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._container.setLayout(self._layout)

        self.setWidget(self._container)

    # ================================================================================== public API
    def AddWidget(self, widget: QWidget, stretch: int = 0) -> None:
        self._layout.addWidget(widget, stretch)

    def InsertWidget(self, index: int, widget: QWidget, stretch: int = 0) -> None:
        self._layout.insertWidget(index, widget, stretch)

    def RemoveWidget(self, widget: QWidget) -> None:
        self._layout.removeWidget(widget)
        widget.hide()
        widget.deleteLater()

    def Clear(self) -> None:
        while self._layout.count():
            lItem = self._layout.takeAt(0)
            if lItem.widget():
                lItem.widget().hide()
                lItem.widget().deleteLater()

    def AddStretch(self, stretch: int = 1) -> None:
        self._layout.addStretch(stretch)

    def Count(self) -> int:
        return self._layout.count()

    # ================================================================================== properties
    @property
    def ContentLayout(self) -> QBoxLayout:
        return self._layout

    @property
    def Container(self) -> QWidget:
        return self._container
