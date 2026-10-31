# ==================================================================================
from __future__ import annotations

# ==================================================================================
from traceback import format_exc
from typing import List, Optional, Tuple, Union

# ==================================================================================
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QFont, QIcon, QMouseEvent, QPixmap, QShowEvent
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
C_ROOT_ICON_SIZE = 22
C_CHILD_ICON_SIZE = 16
C_ROOT_FONT_PT = 12
C_CHILD_FONT_PT = 10
C_ITEM_MARGIN: Tuple[int, int, int, int] = (8, 8, 8, 8)
C_CHILD_INDENT = 20
C_COLLAPSED_WIDTH = 48
C_DEFAULT_ICON = "logo.png"
# ==================================================================================


# ==================================================================================
@workflow
class SideBarMenuItem(SideBarItem):
    OBJECT_NAME = "W_SIDEBAR_MENU_ITEM"

    clicked = Signal(object)
    toggled = Signal(object, bool)

    def __init__(
        self,
        title: str,
        icon: Optional[Union[QIcon, QPixmap, str]] = None,
        role: eSideBarMenuRole = eSideBarMenuRole.Leaf,
        rootIconSize: int = C_ROOT_ICON_SIZE, childIconSize: int = C_CHILD_ICON_SIZE,
        rootFontPt: int = C_ROOT_FONT_PT, childFontPt: int = C_CHILD_FONT_PT,
        itemMargins: Tuple[int, int, int, int] = C_ITEM_MARGIN,
        childIndent: int = C_CHILD_INDENT, collapsedWidth: int = C_COLLAPSED_WIDTH,
        *args, **kwargs,
    ) -> None:
        if icon is None:
            icon = getICONPath(C_DEFAULT_ICON)
        super().__init__(*args, **kwargs)
        self._titleText: str = title
        self._iconData = icon
        self._role: eSideBarMenuRole = role
        self._rootIconSize: int = int(rootIconSize)
        self._childIconSize: int = int(childIconSize)
        self._rootFontPt: int = int(rootFontPt) if int(rootFontPt) > 0 else C_ROOT_FONT_PT
        self._childFontPt: int = int(childFontPt) if int(childFontPt) > 0 else C_CHILD_FONT_PT
        self._itemMargins: Tuple[int, int, int, int] = itemMargins
        self._childIndent: int = int(childIndent)
        self._collapsedWidth: int = int(collapsedWidth)
        self._chromeCollapsed: bool = False
        self._expanded: bool = True
        self._selected: bool = False
        self._children: List[SideBarMenuItem] = []
        self._parentItem: Optional[SideBarMenuItem] = None
        self._body: Optional[QWidget] = None
        self._bodyLayout: Optional[QBoxLayout] = None
        self._iconWidget: Optional[Icon] = None
        self._titleWidget: Optional[Title] = None

    def _isChild(self) -> bool:
        return self._parentItem is not None

    def _effectiveIconSize(self) -> int:
        return self._childIconSize if self._isChild() else self._rootIconSize

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        if self._chromeCollapsed:
            self._applyCollapsedChrome()
        else:
            self._applyExpandedChrome()

    def _applyHierarchyVisuals(self) -> None:
        iconSize = self._effectiveIconSize()
        if self._iconWidget is not None:
            self._iconWidget.setFixedSize(QSize(iconSize, iconSize))

        if self._titleWidget is not None:
            # Never call setPointSize with <= 0 (Qt: QFont::setPointSize Point size <= 0).
            pt = self._childFontPt if self._isChild() else self._rootFontPt
            if pt <= 0:
                pt = C_CHILD_FONT_PT if self._isChild() else C_ROOT_FONT_PT
            pt = max(1, int(pt))
            base = self._titleWidget.font()
            font = QFont(base.family() or "Segoe UI")
            font.setPointSize(pt)
            font.setBold(not self._isChild())
            if base.italic():
                font.setItalic(True)
            self._titleWidget.setFont(font)

    def _hierarchyMargins(self) -> Tuple[int, int, int, int]:
        left, top, right, bottom = self._itemMargins
        if self._isChild():
            left = left + self._childIndent
        return (left, top, right, bottom)

    def _applyExpandedChrome(self) -> None:
        if self._layout is None:
            return
        self._layout.setContentsMargins(*self._hierarchyMargins())
        if self._titleWidget is not None:
            self._titleWidget.setMinimumWidth(0)
            self._titleWidget.setVisible(True)
            self._titleWidget.show()
        self._applyHierarchyVisuals()

    def _applyCollapsedChrome(self) -> None:
        if self._layout is None:
            return
        # Icon-only rail
        if self._titleWidget is not None:
            self._titleWidget.hide()
        hPad = max(0, (self._collapsedWidth - self._effectiveIconSize()) // 2)
        top = self._itemMargins[1]
        bottom = self._itemMargins[3]
        self._layout.setContentsMargins(hPad, top, hPad, bottom)
        self._applyHierarchyVisuals()

    def setChromeCollapsed(self, collapsed: bool) -> None:
        self._chromeCollapsed = bool(collapsed)
        if self._chromeCollapsed:
            self._applyCollapsedChrome()
        else:
            self._applyExpandedChrome()

    def applyMetrics(
        self,
        *,
        rootIconSize: Optional[int] = None,
        childIconSize: Optional[int] = None,
        rootFontPt: Optional[int] = None,
        childFontPt: Optional[int] = None,
        itemMargins: Optional[Tuple[int, int, int, int]] = None,
        childIndent: Optional[int] = None,
        collapsedWidth: Optional[int] = None,
    ) -> None:
        if rootIconSize is not None:
            self._rootIconSize = int(rootIconSize)
        if childIconSize is not None:
            self._childIconSize = int(childIconSize)
        if rootFontPt is not None:
            pt = int(rootFontPt)
            self._rootFontPt = pt if pt > 0 else C_ROOT_FONT_PT
        if childFontPt is not None:
            pt = int(childFontPt)
            self._childFontPt = pt if pt > 0 else C_CHILD_FONT_PT
        if itemMargins is not None:
            self._itemMargins = itemMargins
        if childIndent is not None:
            self._childIndent = int(childIndent)
        if collapsedWidth is not None:
            self._collapsedWidth = int(collapsedWidth)
        if self._chromeCollapsed:
            self._applyCollapsedChrome()
        else:
            self._applyExpandedChrome()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        super().mousePressEvent(event)
        self.clicked.emit(self)
