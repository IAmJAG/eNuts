# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy, QWidget

# ==================================================================================
from jAGQt.icons import MakeArrowLeftIcon, MakeArrowRightIcon
from jAGQt.types import DockPosition

# ==================================================================================
from ....utilities import newLayout
from ...components import ComponentBase

# ==================================================================================
from .__sideBarIcon import SideBarIcon


# ==================================================================================
class SideBarDockControl(QWidget, ComponentBase):
    """Bottom dock flip control.

    Dock left  → right arrow at bottom-right edge
    Dock right → left arrow at bottom-left edge
    """

    DockFlipRequested = Signal()

    def __init__(
        self,
        dockPosition: DockPosition = DockPosition.Left,
        iconSize: int = 16,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)

        self.setObjectName("SideBarDockControl")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._dockPosition: DockPosition = dockPosition
        self._iconSize: int = max(1, int(iconSize))

        self._arrow: SideBarIcon = SideBarIcon(
            icon=None,
            iconSize=self._iconSize,
            parent=self,
        )
        self._arrow.setObjectName("SideBarDockArrow")
        self._arrow.setCursor(Qt.CursorShape.PointingHandCursor)
        self._arrow.mousePressEvent = self._onArrowClicked  # type: ignore

        self._layout: QHBoxLayout = newLayout(
            QHBoxLayout,
            spacing=0,
            margins=(4, 4, 4, 4),
        )
        self.setLayout(self._layout)
        self._rebuild()

    # ==================================================================================
    def SetDockPosition(self, position: DockPosition) -> None:
        if position is self._dockPosition:
            return
        self._dockPosition = position
        self._rebuild()

    @property
    def DockPosition(self) -> DockPosition:
        return self._dockPosition

    # ==================================================================================
    def _rebuild(self) -> None:
        while self._layout.count():
            self._layout.takeAt(0)

        if self._dockPosition is DockPosition.Left:
            self._arrow.SetIcon(MakeArrowRightIcon(self._iconSize))
            self._layout.addStretch(1)
            self._layout.addWidget(self._arrow)
        else:
            self._arrow.SetIcon(MakeArrowLeftIcon(self._iconSize))
            self._layout.addWidget(self._arrow)
            self._layout.addStretch(1)

        self.setProperty(
            "dockSide",
            "left" if self._dockPosition is DockPosition.Left else "right",
        )
        self.style().unpolish(self)
        self.style().polish(self)

    def _onArrowClicked(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.DockFlipRequested.emit()
