# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Callable, Optional

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPixmap


# ==================================================================================
C_DEFAULT_ICON_COLOR = QColor("#E8E8E8")


# ==================================================================================
def NormalizeIconSize(iconSize: int) -> int:
    """Icon size is always a single square edge length."""
    return max(1, int(iconSize))


def ResolveIconColor(color: Optional[QColor] = None) -> QColor:
    return color if color is not None else QColor(C_DEFAULT_ICON_COLOR)


def CreateSquarePixmap(iconSize: int) -> QPixmap:
    lSize: int = NormalizeIconSize(iconSize)
    lPixmap: QPixmap = QPixmap(lSize, lSize)
    lPixmap.fill(Qt.GlobalColor.transparent)
    return lPixmap


def PaintSquareIcon(
    iconSize: int,
    paint: Callable[[QPainter, int, QColor], None],
    color: Optional[QColor] = None,
) -> QPixmap:
    """Allocate a square pixmap and invoke *paint(painter, size, color)*."""
    lSize: int = NormalizeIconSize(iconSize)
    lColor: QColor = ResolveIconColor(color)
    lPixmap: QPixmap = CreateSquarePixmap(lSize)
    lPainter: QPainter = QPainter(lPixmap)
    lPainter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    paint(lPainter, lSize, lColor)
    lPainter.end()
    return lPixmap
