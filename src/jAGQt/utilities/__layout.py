# ==================================================================================
# src/jAGQt/utilities/__layout.py
# ==================================================================================
from typing import List, Optional, Set, Tuple, overload

# ==================================================================================
from PySide6.QtCore import QMargins
from PySide6.QtWidgets import (
    QBoxLayout,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLayout,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)


# ==================================================================================
@overload
def newLayout(
    layout: type[QBoxLayout],
    spacing: int = 0,
    margins: tuple[int, int, int, int] | int = (0, 0, 0, 0),
    direction: QBoxLayout.Direction = QBoxLayout.Direction.TopToBottom,
) -> QBoxLayout: ...


@overload
def newLayout(
    layout: type[QLayout],
    spacing: int = 0,
    margins: tuple[int, int, int, int] | int = (0, 0, 0, 0),
    direction: None = None,
) -> QLayout: ...


def newLayout(
    layout: type[QLayout],
    spacing: int = 0,
    margins: tuple[int, int, int, int] | int = (0, 0, 0, 0),
    direction: Optional[QBoxLayout.Direction] = None,
) -> QLayout:
    """Create a layout with spacing and margins applied.

    Prefer ``QBoxLayout`` + ``direction``. ``QVBoxLayout`` / ``QHBoxLayout``
    do not accept Direction in ``__init__``; they are constructed bare and
    optionally ``setDirection`` is applied only for true ``QBoxLayout``.
    """
    if layout is QBoxLayout or (
        issubclass(layout, QBoxLayout)
        and layout not in (QVBoxLayout, QHBoxLayout)
        and not issubclass(layout, (QVBoxLayout, QHBoxLayout))
    ):
        lDirection = (
            direction
            if direction is not None
            else QBoxLayout.Direction.TopToBottom
        )
        lLayout: QLayout = layout(lDirection)
    elif issubclass(layout, QBoxLayout):
        # QVBoxLayout / QHBoxLayout: no Direction ctor arg.
        lLayout = layout()
        if direction is not None and hasattr(lLayout, "setDirection"):
            lLayout.setDirection(direction)
    else:
        if direction is not None:
            raise TypeError(
                "direction is only supported when layout is a QBoxLayout subclass"
            )
        lLayout = layout()

    if isinstance(margins, int):
        lLayout.setContentsMargins(margins, margins, margins, margins)
    else:
        lLayout.setContentsMargins(*margins)

    lLayout.setSpacing(spacing)
    return lLayout


def contentMargins(values: List[int] | Tuple[int, ...] | Set[int] | int) -> QMargins:
    if isinstance(values, int):
        return QMargins(values, values, values, values)

    if isinstance(values, Tuple | Set):
        values = list(values)

    if isinstance(values, list):
        lLen = len(values)
        if lLen == 1:
            return QMargins(values[0], values[0], values[0], values[0])

        elif lLen == 2:
            return QMargins(values[0], values[1], values[0], values[1])

        elif lLen == 4:
            return QMargins(values[0], values[1], values[2], values[3])

    raise ValueError(
        "Square values must be an int, or a list, tuple, or set of length 1, 2, or 4."
    )


def _findLayoutParent(root: QLayout | None, target: QLayout) -> tuple[QLayout | None, int]:
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
    parent.takeAt(index)

    if isinstance(parent, QBoxLayout):
        parent.insertLayout(index, newLayout)
    elif isinstance(parent, QFormLayout):
        parent.insertRow(index, newLayout)
    elif isinstance(parent, QGridLayout):
        parent.addLayout(newLayout, 0, 0)
    else:
        parent.addChildLayout(newLayout)


def replaceLayout(widget: QWidget, oldLayout: QLayout | None, newLayout: QLayout) -> None:
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
