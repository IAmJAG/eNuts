# ==================================================================================
from __future__ import annotations

# ==================================================================================
from traceback import format_exc
from typing import List, Optional, Union

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
from .__sideBarMenuItem import SideBarMenuItem

# ==================================================================================
QSPolicy = QSizePolicy.Policy
StyleBackground = Qt.WidgetAttribute.WA_StyledBackground
# ==================================================================================


# ==================================================================================
@workflow
class SideBarMenu(ComponentBase, ObjectName, QScrollArea):
    """Scrollable list of top-level SideBarMenuItems (headers with optional leaves)."""

    OBJECT_NAME = "W_SIDEBAR_MENU"

    selectionChanged = Signal(object)  # SideBarMenuItem | None

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._items: List[SideBarMenuItem] = []
        self._selected: Optional[SideBarMenuItem] = None
        self._column: Optional[QWidget] = None
        self._columnLayout: Optional[QBoxLayout] = None

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

    def _insertBeforeStretch(self, widget: QWidget) -> None:
        layout = self._columnLayout
        if layout is None:
            raise RuntimeError("SideBarMenu UI not initialized")
        # stretch is last item
        layout.insertWidget(max(0, layout.count() - 1), widget, stretch=0)

    def addItem(
        self,
        item: Union[SideBarMenuItem, str],
        icon: Optional[Union[QIcon, QPixmap, str]] = None,
        role: eSideBarMenuRole = eSideBarMenuRole.Header,
    ) -> SideBarMenuItem:
        if isinstance(item, str):
            row = SideBarMenuItem(caption=item, icon=icon, role=role)
        else:
            row = item

        self._items.append(row)
        self._insertBeforeStretch(row)
        row.attachBodyTo(self._columnLayout)
        # body is inserted after row; stretch still last — re-order body before stretch
        layout = self._columnLayout
        if layout is not None and row._body is not None:
            layout.removeWidget(row._body)
            # place body immediately after row
            rowIndex = -1
            for i in range(layout.count()):
                if layout.itemAt(i).widget() is row:
                    rowIndex = i
                    break
            if rowIndex >= 0:
                layout.insertWidget(rowIndex + 1, row._body, stretch=0)

        row.selectionRequested.connect(self._onSelectionRequested)
        return row

    def clear(self) -> None:
        layout = self._columnLayout
        if layout is None:
            return
        for item in list(self._items):
            item.selectionRequested.disconnect(self._onSelectionRequested)
            item.clearChildren()
        self._items.clear()
        self._selected = None
        while layout.count() > 1:  # keep trailing stretch
            taken = layout.takeAt(0)
            w = taken.widget()
            if w is not None:
                w.setParent(None)
        self.selectionChanged.emit(None)

    def _onSelectionRequested(self, item: object) -> None:
        if not isinstance(item, SideBarMenuItem):
            return
        self._setSelected(item)

    def _setSelected(self, item: SideBarMenuItem) -> None:
        previous = self._selected
        if previous is item and item.Selected:
            return

        # clear previous selection + ancestor flags
        for top in self._items:
            top.Selected = False
            top.AncestorSelected = False
            for child in top.Children:
                child.Selected = False
                child.AncestorSelected = False

        item.Selected = True
        if item.Role is eSideBarMenuRole.Leaf:
            for top in self._items:
                if item in top.Children:
                    top.AncestorSelected = True
                    break

        self._selected = item
        self.selectionChanged.emit(item)

    # ==================================================================================
    @property
    def Items(self) -> List[SideBarMenuItem]:
        return list(self._items)

    @property
    def SelectedItem(self) -> Optional[SideBarMenuItem]:
        return self._selected
