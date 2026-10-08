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
def MakeCloseIcon(iconSize: int, color: Optional[QColor] = None) -> QIcon:
    """Close (X) icon. Always square."""

    def _paint(painter: QPainter, size: int, iconColor: QColor) -> None:
        lPen: QPen = QPen(iconColor)
        lPen.setWidthF(max(1.0, size * 0.08))
        lPen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(lPen)
        lMargin: float = size * 0.26
        painter.drawLine(
            QPointF(lMargin, lMargin),
            QPointF(size - lMargin, size - lMargin),
        )
        painter.drawLine(
            QPointF(size - lMargin, lMargin),
            QPointF(lMargin, size - lMargin),
        )

    return QIcon(PaintSquareIcon(iconSize, _paint, color))
