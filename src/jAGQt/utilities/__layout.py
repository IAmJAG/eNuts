# ==================================================================================
# src/jAGQt/utilities/__layout.py
# ==================================================================================
from typing import List, Set, Tuple

# ==================================================================================
from PySide6.QtCore import QMargins
from PySide6.QtWidgets import QBoxLayout, QFormLayout, QGridLayout, QLayout, QMainWindow, QWidget


# ==================================================================================
def newLayout(layout: type[QLayout], spacing=0, margins=(0, 0, 0, 0)) -> QLayout:
    lLayout = layout()
    lLayout.setContentsMargins(*margins)
    lLayout.setSpacing(spacing)
    return lLayout


def contentMargins(values: List[int] | Tuple[int, ...] | Set[int] | int) -> QMargins:
    if isinstance(values, int):
        return QMargins(values, values, values, values)

    if isinstance(values, Tuple | Set):
        values = list(values)

    # Handle list
    if isinstance(values, list):
        lLen = len(values)
        if lLen == 1:
            return QMargins(values[0], values[0], values[0], values[0])

        elif lLen == 2:
            return QMargins(values[0], values[1], values[0], values[1])

        elif lLen == 4:
            return QMargins(values[0], values[1], values[2], values[3])

    raise ValueError("Square values must be an int, or a list, tuple, or set of length 1, 2, or 4.")


def _findLayoutParent(root: QLayout | None, target: QLayout) -> tuple[QLayout | None, int]:
    """Return (parentLayout, index) where parentLayout holds target, or (None, -1)."""
    if root is None or root is target:
        return None, -1

    for lIndex in range(root.count()):
        lItem = root.itemAt(lIndex)
        if lItem is None:
            continue

        lChild = lItem.layout()
        if lChild is target:
            return root, lIndex

        if lChild is not None:
            lFound, lFoundIndex = _findLayoutParent(lChild, target)
            if lFound is not None:
                return lFound, lFoundIndex

    return None, -1


def _replaceNestedLayout(parent: QLayout, index: int, newLayout: QLayout) -> None:
    """Remove layout at index and insert newLayout at the same slot."""
    parent.takeAt(index)

    if isinstance(parent, QBoxLayout):
        parent.insertLayout(index, newLayout)
    elif isinstance(parent, QFormLayout):
        parent.insertRow(index, newLayout)
    elif isinstance(parent, QGridLayout):
        # Grid loses row/col unless recorded; fall back to addLayout
        parent.addLayout(newLayout, 0, 0)
    else:
        parent.addChildLayout(newLayout)


def replaceLayout(widget: QWidget, oldLayout: QLayout | None, newLayout: QLayout) -> None:
    """Install newLayout on widget, replacing oldLayout in its exact nesting position when present.

    Existing layouts are detached with ``setParent(None)`` instead of being handed to a
    temporary QWidget: transferring ownership to a throwaway widget lets its C++ destructor
    run immediately and delete the layout, leaving the real widget with a dangling pointer.
    """
    # A QMainWindow owns a Qt-internal QMainWindowLayout which must never be detached from
    # its window, so the layout swap happens on the central widget instead.
    if isinstance(widget, QMainWindow):
        lCentral: QWidget = widget.centralWidget()
        if lCentral is None:
            lCentral = QWidget()
            widget.setCentralWidget(lCentral)
        widget = lCentral

    if oldLayout is None or oldLayout is newLayout:
        lTop = widget.layout()
        if lTop is not None and lTop is not newLayout:
            lTop.setParent(None)
        widget.setLayout(newLayout)
        return

    lTop = widget.layout()
    if lTop is oldLayout:
        oldLayout.setParent(None)
        widget.setLayout(newLayout)
        return

    lParent, lIndex = _findLayoutParent(lTop, oldLayout)
    if lParent is not None and lIndex >= 0:
        _replaceNestedLayout(lParent, lIndex, newLayout)
        return

    if lTop is not None and lTop is not newLayout:
        lTop.setParent(None)
    widget.setLayout(newLayout)
