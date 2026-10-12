# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QMouseEvent
from PySide6.QtWidgets import QBoxLayout, QSizePolicy, QWidget

# ==================================================================================
from jAGFx.workflow import workflow

# ==================================================================================
from ....icons import MakeArrowLeftIcon, MakeArrowRightIcon
from ....icons.animations import IconTransposeAnimation
from ....utilities import newLayout
from ...components import ComponentBase
from ..types import SideBarDockPosition

# ==================================================================================
from .__icon import Icon as SideBarIcon


# ==================================================================================
@workflow
class DockControl(QWidget, ComponentBase):
    OBJECT_NAME = "W_DOCK_CONTROL"
    DockFlipRequested = Signal()

    def __init__(
        self, dockPosition: SideBarDockPosition = SideBarDockPosition.Left,
        iconSize: int = 16, *args, **kwargs,
    ) -> None:
        OBJNAME: str = kwargs.pop("objectName", self.OBJECT_NAME)
        super().__init__(objectName=OBJNAME, *args, **kwargs)

        self._dockPosition: SideBarDockPosition = dockPosition
        self._iconSize: int = max(1, int(iconSize))

    def _wInitializeUI(self):
        iconSize: int = self._iconSize

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        OBJNAME: str = "W_SIDEBAR_ICON"
        arrow: SideBarIcon = SideBarIcon(icon=None, iconSize=iconSize)
        arrow.setObjectName(OBJNAME)
        arrow.setCursor(Qt.CursorShape.PointingHandCursor)
        arrow.mousePressEvent = self._onArrowClicked

        self._arrow: SideBarIcon = arrow

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
        self._pendingPosition: Optional[SideBarDockPosition] = None

        self._rebuild(animate=False)

    # ==================================================================================
    def setDockPosition(self, position: SideBarDockPosition, animate: bool = True) -> None:
        if position is self._dockPosition:
            return
        if animate:
            self._pendingPosition = position
            lCurrent: QIcon = (
                MakeArrowRightIcon(self._iconSize)
                if self._dockPosition is SideBarDockPosition.Left
                else MakeArrowLeftIcon(self._iconSize)
            )
            self._transpose.SetIcon(lCurrent)
            self._transpose.SetIconSize(self._iconSize)
            self._transpose.start()
        else:
            self._dockPosition = position
            self._rebuild(animate=False)

    @property
    def dockPosition(self) -> SideBarDockPosition:
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

        if self._dockPosition is SideBarDockPosition.Left:
            self._arrow.setIcon(MakeArrowRightIcon(self._iconSize))
            self._layout.addStretch(1)
            self._layout.addWidget(self._arrow)
        else:
            self._arrow.setIcon(MakeArrowLeftIcon(self._iconSize))
            self._layout.addWidget(self._arrow)
            self._layout.addStretch(1)

        self.setProperty(
            "dockSide",
            "left" if self._dockPosition is SideBarDockPosition.Left else "right",
        )
        self.style().unpolish(self)
        self.style().polish(self)

    def _onArrowClicked(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.DockFlipRequested.emit()
