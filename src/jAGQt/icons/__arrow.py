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
def _paintChevron(
    painter: QPainter,
    size: int,
    iconColor: QColor,
    pointRight: bool,
) -> None:
    lPen: QPen = QPen(iconColor)
    lPen.setWidthF(max(1.0, size * 0.10))
    lPen.setCapStyle(Qt.PenCapStyle.RoundCap)
    lPen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(lPen)

    lCx: float = size * 0.50
    lCy: float = size * 0.50
    lDx: float = size * 0.16
    lDy: float = size * 0.22

    if pointRight:
        lTip = QPointF(lCx + lDx, lCy)
        lTop = QPointF(lCx - lDx, lCy - lDy)
        lBot = QPointF(lCx - lDx, lCy + lDy)
    else:
        lTip = QPointF(lCx - lDx, lCy)
        lTop = QPointF(lCx + lDx, lCy - lDy)
        lBot = QPointF(lCx + lDx, lCy + lDy)

    painter.drawLine(lTop, lTip)
    painter.drawLine(lBot, lTip)


# ==================================================================================
def MakeArrowRightIcon(iconSize: int, color: Optional[QColor] = None) -> QIcon:
    """Right-pointing chevron. Always square."""

    def _paint(painter: QPainter, size: int, iconColor: QColor) -> None:
        _paintChevron(painter, size, iconColor, pointRight=True)

    return QIcon(PaintSquareIcon(iconSize, _paint, color))


def MakeArrowLeftIcon(iconSize: int, color: Optional[QColor] = None) -> QIcon:
    """Left-pointing chevron. Always square."""

    def _paint(painter: QPainter, size: int, iconColor: QColor) -> None:
        _paintChevron(painter, size, iconColor, pointRight=False)

    return QIcon(PaintSquareIcon(iconSize, _paint, color))
