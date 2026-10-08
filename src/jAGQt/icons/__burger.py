# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPen

# ==================================================================================
from .__base import PaintSquareIcon


# ==================================================================================
def MakeBurgerIcon(iconSize: int, color: Optional[QColor] = None) -> QIcon:
    """Hamburger icon — three horizontal bars. Always square."""

    def _paint(painter: QPainter, size: int, iconColor: QColor) -> None:
        lPen: QPen = QPen(iconColor)
        lPen.setWidthF(max(1.0, size * 0.08))
        lPen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(lPen)
        lMargin: float = size * 0.22
        for lY in (size * 0.30, size * 0.50, size * 0.70):
            painter.drawLine(QPointF(lMargin, lY), QPointF(size - lMargin, lY))

    return QIcon(PaintSquareIcon(iconSize, _paint, color))
