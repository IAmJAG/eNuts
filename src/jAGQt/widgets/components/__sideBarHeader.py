# ==================================================================================
# src/jAGQt/widgets/components/__sideBarHeader.py
# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QBoxLayout, QSizePolicy, QWidget

# ==================================================================================
from jAGQt.types.components import ComponentBase
from jAGQt.utilities import newLayout

# ==================================================================================
from .__sideBarIcon import SideBarIcon
from .__sideBarText import SideBarText


# ==================================================================================
class SideBarHeader(QWidget, ComponentBase):
    """Independent header region for the SideBar (title + optional collapse control)."""

    CollapseRequested = Signal()

    def __init__(
        self,
        title: str = "",
        icon: Optional[object] = None,
        iconSize: int = 20,
        showCollapseButton: bool = True,
        spacing: int = 8,
        parent: Optional[QWidget] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)

        self.setObjectName("SideBarHeader")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._showCollapseButton: bool = showCollapseButton

        self._iconWidget = SideBarIcon(icon=icon, iconSize=iconSize, parent=self)
        self._titleWidget = SideBarText(text=title, parent=self)
        self._titleWidget.setObjectName("SideBarHeaderTitle")

        # Simple collapse indicator (text for now – can be replaced by icon later)
        self._collapseIndicator = SideBarText(text="⟨", parent=self)
        self._collapseIndicator.setObjectName("SideBarHeaderCollapse")
        self._collapseIndicator.setCursor(Qt.CursorShape.PointingHandCursor)
        self._collapseIndicator.setFixedWidth(24)
        self._collapseIndicator.setAlignment(
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
        )
        self._collapseIndicator.mousePressEvent = self._onCollapseClicked  # type: ignore

        self._layout: QBoxLayout = newLayout(
            QBoxLayout, spacing=spacing, margins=(8, 8, 8, 8)
        )
        self._layout.setDirection(QBoxLayout.Direction.LeftToRight)
        self.setLayout(self._layout)

        self._rebuild()

    # ================================================================================== public API
    def SetTitle(self, title: str) -> None:
        self.Title = title

    def SetIcon(self, icon) -> None:
        self._iconWidget.SetIcon(icon)

    # ================================================================================== properties
    @property
    def Title(self) -> str:
        return self._titleWidget.Text

    @Title.setter
    def Title(self, value: str) -> None:
        self._titleWidget.Text = value

    @property
    def ShowCollapseButton(self) -> bool:
        return self._showCollapseButton

    @ShowCollapseButton.setter
    def ShowCollapseButton(self, value: bool) -> None:
        if value == self._showCollapseButton:
            return
        self._showCollapseButton = bool(value)
        self._rebuild()

    @property
    def IconWidget(self) -> SideBarIcon:
        return self._iconWidget

    @property
    def TitleWidget(self) -> SideBarText:
        return self._titleWidget

    # ================================================================================== private
    def _rebuild(self) -> None:
        while self._layout.count():
            lItem = self._layout.takeAt(0)
            if lItem.widget():
                lItem.widget().setParent(None)

        self._layout.addWidget(self._iconWidget)
        self._layout.addWidget(self._titleWidget, 1)

        if self._showCollapseButton:
            self._layout.addWidget(self._collapseIndicator)

    def _onCollapseClicked(self, event) -> None:
        self.CollapseRequested.emit()
