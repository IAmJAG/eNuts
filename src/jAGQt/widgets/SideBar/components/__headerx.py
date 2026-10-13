# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Dict, Optional, Union

# ==================================================================================
from PySide6.QtCore import QEvent, QObject, Qt, Signal, SignalInstance
from PySide6.QtGui import QIcon, QMouseEvent, QPixmap
from PySide6.QtWidgets import QSizePolicy

# ==================================================================================
from jAGFx.workflow import workflow
from jAGQt.icons import MakeBurgerIcon, MakeCloseIcon

# ==================================================================================
from ...header import Header
from ...icon import StatefullIcon
from ..types import sideBarState

# ==================================================================================
QPolicy = QSizePolicy.Policy
# ==================================================================================


# ==================================================================================
class SideBarHeaderx(Header):
    CollapseRequested: SignalInstance = Signal()
    def __init__(
        self, title: Optional[str] = None, iconSize: int = 24, *args, **kwargs,
    ) -> None:        
        super().__init__(title=title, iconSize=iconSize, *args, **kwargs)
        self._title: str = title if title is not None else ""
        self._state: sideBarState = sideBarState.Expanded

    def _wInitializeUI(self) -> None:        
        iconSize: int = self.iconSize

        burgerIcon: QIcon = MakeBurgerIcon(iconSize)
        closeIcon: QIcon = MakeCloseIcon(iconSize)

        icons: Dict[sideBarState, Optional[Union[QIcon, QPixmap, str]]] = {
            sideBarState.Collapsed: closeIcon,
            sideBarState.Expanded: burgerIcon,
        }
        toggleIcon: StatefullIcon[sideBarState] = StatefullIcon[sideBarState](icons)
        toggleIcon.setCursor(Qt.CursorShape.PointingHandCursor)

        super()._wInitializeUI(False)
        self._icon: StatefullIcon[sideBarState] = toggleIcon
        self._rebuildLayout()

    @property
    def state(self) -> sideBarState:
        return self._state

    @state.setter
    def state(self, value: sideBarState) -> None:
        self._state = value
        self._icon.state = value        
        self._rebuildLayout()

    # ==================================================================================
    @property
    def title(self) -> str:
        return super().title

    @title.setter
    def title(self, value: str) -> None:
        super().title = value if value is not None else ""

    @property
    def iconSize(self) -> int:
        return self._icon.iconSize
    
    @iconSize.setter
    def iconSize(self, value: int) -> None:
        size = max(1, int(value))
        if size == self._icon.iconSize: return
        self._icon.iconSize = size

    # ==================================================================================
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if (
            watched is self._icon
            and event.type() == QEvent.Type.MouseButtonPress
            and isinstance(event, QMouseEvent)
            and event.button() == Qt.MouseButton.LeftButton
        ):
            self.CollapseRequested.emit()
            return True
        
        return super().eventFilter(watched, event)

    def _rebuildLayout(self) -> None:
        super()._rebuildLayout()
    