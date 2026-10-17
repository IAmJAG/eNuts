# ==================================================================================
from __future__ import annotations

# ==================================================================================
from traceback import format_exc
from typing import List, Optional, Tuple, Union

# ==================================================================================
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon, QMouseEvent, QPixmap
from PySide6.QtWidgets import QBoxLayout, QSizePolicy, QWidget

# ==================================================================================
from jAGFx.workflow import workflow
from utilities.io import getICONPath

# ==================================================================================
from ....utilities import newLayout
from ...icon import Icon
from ...text import Title
from ..components import SideBarItem
from .__eSideBarMenuRole import eSideBarMenuRole

# ==================================================================================
QSPolicy = QSizePolicy.Policy
C_ICON_SIZE = 20
C_HEADER_MARGIN: Tuple[int, int, int, int] = (8, 8, 8, 8)
C_LEAF_MARGIN: Tuple[int, int, int, int] = (28, 6, 8, 6)
C_DEFAULT_ICON = "logo.png"
# ==================================================================================


# ==================================================================================
def _defaultIconPath() -> str:
    return getICONPath(C_DEFAULT_ICON)


# ==================================================================================
@workflow
class SideBarMenuItem(SideBarItem):
    """One menu row. Sizing (margins, icon) comes from metrics / SideBarOptions."""

    OBJECT_NAME = "W_SIDEBAR_MENU_ITEM"

    clicked = Signal(object)
    toggled = Signal(object, bool)
    selectionRequested = Signal(object)

    def __init__(
        self,
        caption: str = "",
        icon: Optional[Union[QIcon, QPixmap, str]] = None,
        role: eSideBarMenuRole = eSideBarMenuRole.Header,
        iconSize: int = C_ICON_SIZE,
        headerMargins: Tuple[int, int, int, int] = C_HEADER_MARGIN,
        leafMargins: Tuple[int, int, int, int] = C_LEAF_MARGIN,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._captionText: str = caption
        if icon is None:
            icon = _defaultIconPath()
        self._iconSource: Optional[Union[QIcon, QPixmap, str]] = icon
        self._role: eSideBarMenuRole = role
        self._iconSize: int = int(iconSize)
        self._headerMargins: Tuple[int, int, int, int] = tuple(headerMargins)  # type: ignore
        self._leafMargins: Tuple[int, int, int, int] = tuple(leafMargins)  # type: ignore
        self._expanded: bool = True
        self._selected: bool = False
        self._children: List[SideBarMenuItem] = []
        self._parentItem: Optional[SideBarMenuItem] = None
        self._body: Optional[QWidget] = None
        self._bodyLayout: Optional[QBoxLayout] = None
        self._iconWidget: Optional[Icon] = None
        self._titleWidget: Optional[Title] = None

    def _wInitializeUI(self) -> None:
        verbose(f"[SideBarMenuItem] _wInitializeUI role={self._role!r}")
        try:
            super()._wInitializeUI()

            caption = self._captionText
            iconSrc = self._iconSource
            role = self._role
            iconSize = self._iconSize
            del self._captionText
            del self._iconSource

            margins = (
                self._leafMargins
                if role is eSideBarMenuRole.Leaf
                else self._headerMargins
            )
            self._layout.setContentsMargins(*margins)

            iconWidget = Icon(icon=iconSrc, objectName=f"{self.OBJECT_NAME}_ICON")
            iconWidget.setFixedSize(QSize(iconSize, iconSize))
            iconWidget.setSizePolicy(QSPolicy.Fixed, QSPolicy.Fixed)

            titleWidget = Title(caption, objectName=f"{self.OBJECT_NAME}_TITLE")

            self._addLeading(iconWidget)
            self._addTextWidget(titleWidget)

            self._iconWidget = iconWidget
            self._titleWidget = titleWidget

            self._setRoleProperty(role)
            self._setSelectedProperty(False)
            self.setCursor(Qt.CursorShape.PointingHandCursor)

            if role is eSideBarMenuRole.Header:
                body = QWidget(self)
                body.setObjectName(f"{self.OBJECT_NAME}_BODY")
                bodyLayout = newLayout(
                    QBoxLayout,
                    spacing=0,
                    margins=(0, 0, 0, 0),
                    direction=QBoxLayout.Direction.TopToBottom,
                )
                body.setLayout(bodyLayout)
                body.hide()
                self._body = body
                self._bodyLayout = bodyLayout
        except Exception as ex:
            error("[SideBarMenuItem] _wInitializeUI FAIL", ex)
            error(f"[SideBarMenuItem] traceback:\n{format_exc()}")
            raise

    def applyMetrics(
        self,
        *,
        iconSize: Optional[int] = None,
        headerMargins: Optional[Tuple[int, int, int, int]] = None,
        leafMargins: Optional[Tuple[int, int, int, int]] = None,
    ) -> None:
        """Re-apply size metrics after construct (e.g. from SideBarOptions)."""
        if iconSize is not None:
            self._iconSize = int(iconSize)
            if self._iconWidget is not None:
                self._iconWidget.setFixedSize(QSize(self._iconSize, self._iconSize))
        if headerMargins is not None:
            self._headerMargins = tuple(headerMargins)  # type: ignore
        if leafMargins is not None:
            self._leafMargins = tuple(leafMargins)  # type: ignore
        if self._layout is not None:
            margins = (
                self._leafMargins
                if self._role is eSideBarMenuRole.Leaf
                else self._headerMargins
            )
            self._layout.setContentsMargins(*margins)

    def _setRoleProperty(self, role: eSideBarMenuRole) -> None:
        self._role = role
        label = "header" if role is eSideBarMenuRole.Header else "leaf"
        self.setProperty("role", label)
        self.style().unpolish(self)
        self.style().polish(self)

    def _setSelectedProperty(self, value: bool) -> None:
        self._selected = value
        self.setProperty("selected", "true" if value else "false")
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                if (
                    self._role is eSideBarMenuRole.Header
                    and len(self._children) > 0
                ):
                    self.Expanded = not self._expanded
                self.selectionRequested.emit(self)
                self.clicked.emit(self)
                event.accept()
                return
            super().mousePressEvent(event)
        except Exception as ex:
            error("[SideBarMenuItem] mousePressEvent FAIL", ex)
            raise

    def addChild(
        self,
        item: Union[SideBarMenuItem, str],
        icon: Optional[Union[QIcon, QPixmap, str]] = None,
    ) -> SideBarMenuItem:
        if self._role is not eSideBarMenuRole.Header:
            raise TypeError("Only header (parent) menu items may own children")

        if isinstance(item, str):
            child = SideBarMenuItem(
                caption=item,
                icon=icon,
                role=eSideBarMenuRole.Leaf,
                iconSize=self._iconSize,
                headerMargins=self._headerMargins,
                leafMargins=self._leafMargins,
            )
        else:
            child = item
            if child.Role is not eSideBarMenuRole.Leaf:
                raise ValueError("Child menu items must have role Leaf (one level only)")
            child.applyMetrics(
                iconSize=self._iconSize,
                headerMargins=self._headerMargins,
                leafMargins=self._leafMargins,
            )

        if self._body is None or self._bodyLayout is None:
            raise RuntimeError("SideBarMenuItem UI not initialized")

        child._parentItem = self
        self._children.append(child)
        self._bodyLayout.addWidget(child)
        if self._expanded:
            self._body.show()
        child.selectionRequested.connect(self.selectionRequested.emit)
        child.clicked.connect(self.clicked.emit)
        return child

    def clearChildren(self) -> None:
        if self._bodyLayout is None:
            return
        for child in list(self._children):
            try:
                child.selectionRequested.disconnect(self.selectionRequested.emit)
                child.clicked.disconnect(self.clicked.emit)
            except Exception:
                pass
            child._parentItem = None
        while self._bodyLayout.count():
            taken = self._bodyLayout.takeAt(0)
            w = taken.widget()
            if w is not None:
                w.setParent(None)
        self._children.clear()
        if self._body is not None:
            self._body.hide()

    def attachBodyTo(self, parentLayout: QBoxLayout) -> None:
        if self._role is not eSideBarMenuRole.Header:
            return
        if self._body is None:
            return
        parentLayout.addWidget(self._body, stretch=0)

    @property
    def Role(self) -> eSideBarMenuRole:
        return self._role

    @property
    def ParentItem(self) -> Optional[SideBarMenuItem]:
        return self._parentItem

    @property
    def Caption(self) -> str:
        if self._titleWidget is None:
            return ""
        return self._titleWidget.Text

    @Caption.setter
    def Caption(self, value: str) -> None:
        if self._titleWidget is not None:
            self._titleWidget.Text = value

    @property
    def Expanded(self) -> bool:
        return self._expanded

    @Expanded.setter
    def Expanded(self, value: bool) -> None:
        value = bool(value)
        if value == self._expanded:
            return
        self._expanded = value
        if self._body is not None:
            self._body.setVisible(value and len(self._children) > 0)
        self.toggled.emit(self, value)

    @property
    def Selected(self) -> bool:
        return self._selected

    @Selected.setter
    def Selected(self, value: bool) -> None:
        self._setSelectedProperty(bool(value))

    @property
    def Children(self) -> List[SideBarMenuItem]:
        return list(self._children)
