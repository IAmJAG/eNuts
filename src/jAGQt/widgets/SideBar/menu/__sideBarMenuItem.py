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
    selectionRequested = Signal(object)

    def __init__(
        self, caption: str = "", icon: Optional[Union[QIcon, QPixmap, str]] = None,
        role: eSideBarMenuRole = eSideBarMenuRole.Header,
        rootIconSize: int = C_ROOT_ICON_SIZE, childIconSize: int = C_CHILD_ICON_SIZE,
        rootFontPt: int = C_ROOT_FONT_PT, childFontPt: int = C_CHILD_FONT_PT,
        itemMargins: Tuple[int, int, int, int] = C_ITEM_MARGIN,
        childIndent: int = C_CHILD_INDENT, collapsedWidth: int = C_COLLAPSED_WIDTH,
        *args, **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._captionText: str = caption
        if icon is None: icon = getICONPath(C_DEFAULT_ICON)
        self._iconSource: Optional[Union[QIcon, QPixmap, str]] = icon
        self._role: eSideBarMenuRole = role
        self._rootIconSize: int = int(rootIconSize)
        self._childIconSize: int = int(childIconSize)
        self._rootFontPt: int = int(rootFontPt) if int(rootFontPt) > 0 else C_ROOT_FONT_PT
        self._childFontPt: int = int(childFontPt) if int(childFontPt) > 0 else C_CHILD_FONT_PT
        self._itemMargins: Tuple[int, int, int, int] = tuple(itemMargins)  # type: ignore
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

    def _wInitializeUI(self) -> None:
        verbose(f"[SideBarMenuItem] _wInitializeUI role={self._role!r}")
        try:
            super()._wInitializeUI()

            caption = self._captionText
            iconSrc = self._iconSource
            role = self._role
            del self._captionText
            del self._iconSource

            iconSize = self._effectiveIconSize()
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
            self._applyHierarchyVisuals()
            self._applyExpandedChrome()

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
            font: QFont = self._titleWidget.font()
            pt = self._childFontPt if self._isChild() else self._rootFontPt
            if pt > 0:
                font.setPointSize(pt)
            font.setBold(not self._isChild())
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
            try:
                self._titleWidget.setText(self._titleWidget.Text)
            except Exception:
                pass
        if self._textColumn is not None:
            for i in range(self._textColumn.count()):
                w = self._textColumn.itemAt(i).widget()
                if w is not None:
                    w.setVisible(True)
                    w.show()
        self.updateGeometry()

    def _applyCollapsedChrome(self) -> None:
        if self._layout is None or self._iconWidget is None:
            return
        if self._titleWidget is not None:
            self._titleWidget.setMinimumWidth(0)
            self._titleWidget.hide()
        if self._textColumn is not None:
            for i in range(self._textColumn.count()):
                w = self._textColumn.itemAt(i).widget()
                if w is not None:
                    w.hide()
        iconSize = self._effectiveIconSize()
        hPad = max(0, (self._collapsedWidth - iconSize) // 2)
        top = self._itemMargins[1]
        bottom = self._itemMargins[3]
        self._layout.setContentsMargins(hPad, top, hPad, bottom)
        self.updateGeometry()

    def _syncBodyVisibility(self) -> None:
        if self._body is None:
            return
        if not self._children:
            self._body.hide()
            return
        if self._chromeCollapsed:
            self._body.show()
            return
        self._body.setVisible(self._expanded)

    def setChromeCollapsed(self, collapsed: bool) -> None:
        self._chromeCollapsed = bool(collapsed)
        if self._chromeCollapsed:
            self._applyCollapsedChrome()
        else:
            self._applyExpandedChrome()
        self._syncBodyVisibility()

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
            self._itemMargins = tuple(itemMargins)  # type: ignore
        if childIndent is not None:
            self._childIndent = int(childIndent)
        if collapsedWidth is not None:
            self._collapsedWidth = int(collapsedWidth)

        self._applyHierarchyVisuals()
        if self._chromeCollapsed:
            self._applyCollapsedChrome()
        else:
            self._applyExpandedChrome()

    def _setRoleProperty(self, role: eSideBarMenuRole) -> None:
        self._role = role
        label = "header" if role is eSideBarMenuRole.Header else "leaf"
        self.setProperty("role", label)
        depth = "child" if self._isChild() else "root"
        self.setProperty("depth", depth)
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
                    and not self._chromeCollapsed
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

        metrics = dict(
            rootIconSize=self._rootIconSize,
            childIconSize=self._childIconSize,
            rootFontPt=self._rootFontPt,
            childFontPt=self._childFontPt,
            itemMargins=self._itemMargins,
            childIndent=self._childIndent,
            collapsedWidth=self._collapsedWidth,
        )

        if isinstance(item, str):
            child = SideBarMenuItem(
                caption=item,
                icon=icon,
                role=eSideBarMenuRole.Leaf,
                **metrics,
            )
        else:
            child = item
            if child.Role is not eSideBarMenuRole.Leaf:
                raise ValueError("Child menu items must have role Leaf (one level only)")
            child.applyMetrics(**metrics)

        if self._body is None or self._bodyLayout is None:
            raise RuntimeError("SideBarMenuItem UI not initialized")

        child._parentItem = self
        child._setRoleProperty(child._role)
        child.applyMetrics(**metrics)
        if self._chromeCollapsed:
            child.setChromeCollapsed(True)

        self._children.append(child)
        self._bodyLayout.addWidget(child)
        self._syncBodyVisibility()
        child.selectionRequested.connect(self.selectionRequested.emit)
        child.clicked.connect(self.clicked.emit)
        return child

    def clearChildren(self) -> None:
        """Remove and destroy all child menu items."""
        if self._bodyLayout is None:
            self._children.clear()
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
            if taken is None:
                continue
            w = taken.widget()
            if w is not None:
                w.hide()
                w.setParent(None)
                w.deleteLater()

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
        self._syncBodyVisibility()
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
