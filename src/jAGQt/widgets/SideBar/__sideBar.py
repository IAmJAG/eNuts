# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QBoxLayout, QSizePolicy, QWidget

# ==================================================================================
from jAGQt.types import DockPosition

# ==================================================================================
from ...utilities import newLayout
from ..components import ComponentBase

# ==================================================================================
from .__options import sideBarConfig
from .components import SideBarDockControl, SideBarHeader


# ==================================================================================
class SideBar(QWidget, ComponentBase):
    """Side bar frame + header + dock control.

    Header and dock control are internal.
    Collapse updates header visuals; width animation wires later via DrawerAnimation.
    """

    CollapseRequested = Signal()
    CollapsedChanged = Signal(bool)
    DockSideChanged = Signal(object)

    def __init__(
        self,
        title: str = "",
        config: Optional[sideBarConfig] = None,
        parent: Optional[QWidget] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)

        self._config: sideBarConfig = config if config is not None else sideBarConfig()
        self._collapsed: bool = bool(self._config.startCollapsed)
        self._dockPosition: DockPosition = self._config.dockPosition

        self.setObjectName("SideBar")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        lWidth: int = self._config.expandedWidth
        self.setFixedWidth(lWidth)
        self.setMinimumWidth(lWidth)
        self.setMaximumWidth(lWidth)

        self._layout: QBoxLayout = newLayout(
            QBoxLayout,
            spacing=0,
            margins=(0, 0, 0, 0),
            direction=QBoxLayout.Direction.TopToBottom,
        )
        self.setLayout(self._layout)

        self._header: SideBarHeader = SideBarHeader(
            title=title,
            iconSize=self._config.iconSize,
            parent=self,
        )
        self._header.CollapseRequested.connect(self._onHeaderCollapseRequested)

        self._contentHost: QWidget = QWidget(self)
        self._contentHost.setObjectName("SideBarContentHost")
        self._contentHost.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        lDockIconSize: int = max(12, min(self._config.iconSize, 18))
        self._dockControl: SideBarDockControl = SideBarDockControl(
            dockPosition=self._dockPosition,
            iconSize=lDockIconSize,
            parent=self,
        )
        self._dockControl.DockFlipRequested.connect(self._onDockFlipRequested)

        self._layout.addWidget(self._header)
        self._layout.addWidget(self._contentHost, 1)
        self._layout.addWidget(self._dockControl)

        self._applyDockProperty()
        if self._collapsed:
            self._header.SetCollapsed(True)

    # ==================================================================================
    def SetTitle(self, title: str) -> None:
        self._header.SetTitle(title)

    def SetCollapsed(self, collapsed: bool) -> None:
        lValue: bool = bool(collapsed)
        if lValue is self._collapsed:
            return
        self._collapsed = lValue
        self._header.SetCollapsed(lValue)
        self.setProperty("collapsed", "true" if lValue else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        self.CollapsedChanged.emit(lValue)

    def ToggleCollapse(self) -> None:
        self.SetCollapsed(not self._collapsed)

    def SetDockSide(self, position: DockPosition) -> None:
        if position is self._dockPosition:
            return
        self._dockPosition = position
        self._dockControl.SetDockPosition(position)
        self._applyDockProperty()
        self.DockSideChanged.emit(position)

    def ToggleDockSide(self) -> None:
        lNext = (
            DockPosition.Right
            if self._dockPosition is DockPosition.Left
            else DockPosition.Left
        )
        self.SetDockSide(lNext)

    # ==================================================================================
    @property
    def Config(self) -> sideBarConfig:
        return self._config

    @property
    def Title(self) -> str:
        return self._header.Title

    @Title.setter
    def Title(self, value: str) -> None:
        self._header.Title = value

    @property
    def Collapsed(self) -> bool:
        return self._collapsed

    @Collapsed.setter
    def Collapsed(self, value: bool) -> None:
        self.SetCollapsed(value)

    @property
    def DockSide(self) -> DockPosition:
        return self._dockPosition

    @DockSide.setter
    def DockSide(self, value: DockPosition) -> None:
        self.SetDockSide(value)

    # ==================================================================================
    def _applyDockProperty(self) -> None:
        self.setProperty(
            "dockSide",
            "left" if self._dockPosition is DockPosition.Left else "right",
        )
        self.style().unpolish(self)
        self.style().polish(self)

    def _onHeaderCollapseRequested(self) -> None:
        self.ToggleCollapse()
        self.CollapseRequested.emit()

    def _onDockFlipRequested(self) -> None:
        self.ToggleDockSide()
