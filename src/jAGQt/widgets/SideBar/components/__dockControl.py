# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QMouseEvent
from PySide6.QtWidgets import QBoxLayout, QSizePolicy, QWidget

# ==================================================================================
from jAGQt.icons import MakeArrowLeftIcon, MakeArrowRightIcon
from jAGQt.icons.animations import IconTransposeAnimation
from jAGQt.types import DockPosition

# ==================================================================================
from ....utilities import newLayout
from ...components import ComponentBase

# ==================================================================================
from .__sideBarIcon import SideBarIcon


# ==================================================================================
class SideBarDockControl(QWidget, ComponentBase):
    """Bottom dock flip control with optional arrow transpose animation."""

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

        self._layout: QBoxLayout = newLayout(
            QBoxLayout,
            spacing=0,
            margins=(4, 4, 4, 4),
            direction=QBoxLayout.Direction.LeftToRight,
        )
        self.setLayout(self._layout)

        self._transpose: IconTransposeAnimation = IconTransposeAnimation(
            target=self._arrow,
            iconSize=self._iconSize,
            durationMs=140,
            parent=self,
        )
        self._transpose.Finished.connect(self._onTransposeFinished)
        self._pendingPosition: Optional[DockPosition] = None

        self._rebuild(animate=False)

    # ==================================================================================
    def SetDockPosition(self, position: DockPosition, animate: bool = True) -> None:
        if position is self._dockPosition:
            return
        if animate:
            self._pendingPosition = position
            lCurrent: QIcon = (
                MakeArrowRightIcon(self._iconSize)
                if self._dockPosition is DockPosition.Left
                else MakeArrowLeftIcon(self._iconSize)
            )
            self._transpose.SetIcon(lCurrent)
            self._transpose.SetIconSize(self._iconSize)
            self._transpose.Start()
        else:
            self._dockPosition = position
            self._rebuild(animate=False)

    @property
    def DockPosition(self) -> DockPosition:
        return self._dockPosition

    # ==================================================================================
    def _onTransposeFinished(self) -> None:
        if self._pendingPosition is not None:
            self._dockPosition = self._pendingPosition
            self._pendingPosition = None
            self._rebuild(animate=False)

    def _rebuild(self, animate: bool = False) -> None:
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
