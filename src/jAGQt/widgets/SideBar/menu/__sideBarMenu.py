# ==================================================================================
from __future__ import annotations

# ==================================================================================
from traceback import format_exc
from typing import List, Optional, Tuple, Union

# ==================================================================================
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QBoxLayout,
    QScrollArea,
    QSizePolicy,
    QWidget,
)

# ==================================================================================
from jAGFx.workflow import workflow

# ==================================================================================
from ....utilities import newLayout
from ...components import ComponentBase, ObjectName
from .__eSideBarMenuRole import eSideBarMenuRole
from .__sideBarMenuItem import (
    C_HEADER_MARGIN,
    C_ICON_SIZE,
    C_LEAF_MARGIN,
    SideBarMenuItem,
)

# ==================================================================================
QSPolicy = QSizePolicy.Policy
StyleBackground = Qt.WidgetAttribute.WA_StyledBackground
# ==================================================================================


# ==================================================================================
@workflow
class SideBarMenu(ComponentBase, ObjectName, QScrollArea):
    """Scrollable list of top-level SideBarMenuItems.

    Row metrics (icon size, header/leaf margins) come from SideBarOptions via
    :meth:`applyMetrics` / SideBar content wiring.
    """

    OBJECT_NAME = "W_SIDEBAR_MENU"

    itemClicked = Signal(object)
    selectionChanged = Signal(object)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._items: List[SideBarMenuItem] = []
        self._selected: Optional[SideBarMenuItem] = None
        self._selectOnClick: bool = True
        self._column: Optional[QWidget] = None
        self._columnLayout: Optional[QBoxLayout] = None
        self._iconSize: int = C_ICON_SIZE
        self._headerMargins: Tuple[int, int, int, int] = C_HEADER_MARGIN
        self._leafMargins: Tuple[int, int, int, int] = C_LEAF_MARGIN

    def _wInitializeUI(self) -> None:
        verbose("[SideBarMenu] _wInitializeUI ENTER")
        try:
            self.setAttribute(StyleBackground, True)
            self.setWidgetResizable(True)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.setFrameShape(QScrollArea.Shape.NoFrame)
            self.setSizePolicy(QSPolicy.Expanding, QSPolicy.Expanding)

            column = QWidget()
            column.setObjectName(f"{self.OBJECT_NAME}_COLUMN")
            columnLayout = newLayout(
                QBoxLayout,
                spacing=0,
                margins=(0, 0, 0, 0),
                direction=QBoxLayout.Direction.TopToBottom,
            )
            columnLayout.addStretch(1)
            column.setLayout(columnLayout)

            self.setWidget(column)
            self._column = column
            self._columnLayout = columnLayout
            verbose("[SideBarMenu] _wInitializeUI EXIT")
        except Exception as ex:
            error("[SideBarMenu] _wInitializeUI FAIL", ex)
            error(f"[SideBarMenu] traceback:\n{format_exc()}")
            raise

    def applyMetrics(
        self,
        *,
        iconSize: int,
        headerMargins: Tuple[int, int, int, int],
        leafMargins: Tuple[int, int, int, int],
    ) -> None:
        """Store metrics and push to existing rows (and future addItem/addChild)."""
        self._iconSize = int(iconSize)
        self._headerMargins = tuple(headerMargins)  # type: ignore
        self._leafMargins = tuple(leafMargins)  # type: ignore
        for top in self._items:
            top.applyMetrics(
                iconSize=self._iconSize,
                headerMargins=self._headerMargins,
                leafMargins=self._leafMargins,
            )
            for child in top.Children:
                child.applyMetrics(
                    iconSize=self._iconSize,
                    headerMargins=self._headerMargins,
                    leafMargins=self._leafMargins,
                )

    def _insertBeforeStretch(self, widget: QWidget) -> None:
        layout = self._columnLayout
        if layout is None:
            raise RuntimeError("SideBarMenu UI not initialized")
        layout.insertWidget(max(0, layout.count() - 1), widget, stretch=0)

    def addItem(
        self,
        item: Union[SideBarMenuItem, str],
        icon: Optional[Union[QIcon, QPixmap, str]] = None,
        role: eSideBarMenuRole = eSideBarMenuRole.Header,
    ) -> SideBarMenuItem:
        if isinstance(item, str):
            row = SideBarMenuItem(
                caption=item,
                icon=icon,
                role=role,
                iconSize=self._iconSize,
                headerMargins=self._headerMargins,
                leafMargins=self._leafMargins,
            )
        else:
            row = item
            row.applyMetrics(
                iconSize=self._iconSize,
                headerMargins=self._headerMargins,
                leafMargins=self._leafMargins,
            )

        self._items.append(row)
        self._insertBeforeStretch(row)
        row.attachBodyTo(self._columnLayout)
        layout = self._columnLayout
        if layout is not None and row._body is not None:
            layout.removeWidget(row._body)
            rowIndex = -1
            for i in range(layout.count()):
                if layout.itemAt(i).widget() is row:
                    rowIndex = i
                    break
            if rowIndex >= 0:
                layout.insertWidget(rowIndex + 1, row._body, stretch=0)

        row.selectionRequested.connect(self._onSelectionRequested)
        row.clicked.connect(self._onItemClicked)
        return row

    def clear(self) -> None:
        layout = self._columnLayout
        if layout is None:
            return
        for item in list(self._items):
            try:
                item.selectionRequested.disconnect(self._onSelectionRequested)
                item.clicked.disconnect(self._onItemClicked)
            except Exception:
                pass
            item.clearChildren()
        self._items.clear()
        self._selected = None
        while layout.count() > 1:
            taken = layout.takeAt(0)
            w = taken.widget()
            if w is not None:
                w.setParent(None)
        self.selectionChanged.emit(None)

    def selectItem(self, item: Optional[SideBarMenuItem]) -> None:
        if item is None:
            self._clearSelectionFlags()
            self._selected = None
            self.selectionChanged.emit(None)
            return

        if item is self._selected and item.Selected:
            return

        self._clearSelectionFlags()
        item.Selected = True
        self._selected = item
        self.selectionChanged.emit(item)

    def _clearSelectionFlags(self) -> None:
        for top in self._items:
            top.Selected = False
            for child in top.Children:
                child.Selected = False

    def _onSelectionRequested(self, item: object) -> None:
        if not isinstance(item, SideBarMenuItem):
            return
        if self._selectOnClick:
            self.selectItem(item)

    def _onItemClicked(self, item: object) -> None:
        if isinstance(item, SideBarMenuItem):
            self.itemClicked.emit(item)

    def parentOf(self, item: SideBarMenuItem) -> Optional[SideBarMenuItem]:
        return item.ParentItem

    @property
    def SelectOnClick(self) -> bool:
        return self._selectOnClick

    @SelectOnClick.setter
    def SelectOnClick(self, value: bool) -> None:
        self._selectOnClick = bool(value)

    @property
    def Items(self) -> List[SideBarMenuItem]:
        return list(self._items)

    @property
    def SelectedItem(self) -> Optional[SideBarMenuItem]:
        return self._selected
