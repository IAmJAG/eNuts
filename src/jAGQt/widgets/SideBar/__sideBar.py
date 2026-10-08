# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QBoxLayout, QSizePolicy, QWidget

# ==================================================================================
from ...utilities import newLayout
from ..components import ComponentBase

# ==================================================================================
from .__options import sideBarConfig


# ==================================================================================
class SideBar(QWidget, ComponentBase):
    """Phase 1 — outer frame only.

    Owns width contract, vertical layout, and two reserved hosts
    (header + content) for later phases. No header or items yet.
    """

    def __init__(
        self,
        config: Optional[sideBarConfig] = None,
        parent: Optional[QWidget] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)

        self._config: sideBarConfig = config if config is not None else sideBarConfig()

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

        # Reserved hosts for Phase 2 (header) and Phase 3 (buttons/content)
        self._headerHost: QWidget = QWidget(self)
        self._headerHost.setObjectName("SideBarHeaderHost")
        self._headerHost.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )

        self._contentHost: QWidget = QWidget(self)
        self._contentHost.setObjectName("SideBarContentHost")
        self._contentHost.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        self._layout.addWidget(self._headerHost)
        self._layout.addWidget(self._contentHost, 1)

    # ==================================================================================
    @property
    def Config(self) -> sideBarConfig:
        return self._config

    @property
    def HeaderHost(self) -> QWidget:
        return self._headerHost

    @property
    def ContentHost(self) -> QWidget:
        return self._contentHost
