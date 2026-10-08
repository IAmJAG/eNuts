# ==================================================================================
from __future__ import annotations

# ==================================================================================
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap


# ==================================================================================
def MakeBurgerIcon(iconSize: int, color: QColor | None = None) -> QIcon:
    """Code-generated hamburger icon (three horizontal bars). Always square."""
    lSize: int = max(1, int(iconSize))
    lPixmap: QPixmap = QPixmap(lSize, lSize)
    lPixmap.fill(Qt.GlobalColor.transparent)

    lColor: QColor = color if color is not None else QColor("#E8E8E8")
    lPen: QPen = QPen(lColor)
    lPen.setWidthF(max(1.0, lSize * 0.08))
    lPen.setCapStyle(Qt.PenCapStyle.RoundCap)

    lPainter: QPainter = QPainter(lPixmap)
    lPainter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    lPainter.setPen(lPen)

    lMargin: float = lSize * 0.22
    lLeft: float = lMargin
    lRight: float = lSize - lMargin
    lYs: tuple[float, float, float] = (
        lSize * 0.30,
        lSize * 0.50,
        lSize * 0.70,
    )
    for lY in lYs:
        lPainter.drawLine(QPointF(lLeft, lY), QPointF(lRight, lY))

    lPainter.end()
    return QIcon(lPixmap)


# ==================================================================================
def MakeCloseIcon(iconSize: int, color: QColor | None = None) -> QIcon:
    """Code-generated close (X) icon. Always square."""
    lSize: int = max(1, int(iconSize))
    lPixmap: QPixmap = QPixmap(lSize, lSize)
    lPixmap.fill(Qt.GlobalColor.transparent)

    lColor: QColor = color if color is not None else QColor("#E8E8E8")
    lPen: QPen = QPen(lColor)
    lPen.setWidthF(max(1.0, lSize * 0.08))
    lPen.setCapStyle(Qt.PenCapStyle.RoundCap)

    lPainter: QPainter = QPainter(lPixmap)
    lPainter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    lPainter.setPen(lPen)

    lMargin: float = lSize * 0.26
    lPainter.drawLine(
        QPointF(lMargin, lMargin),
        QPointF(lSize - lMargin, lSize - lMargin),
    )
    lPainter.drawLine(
        QPointF(lSize - lMargin, lMargin),
        QPointF(lMargin, lSize - lMargin),
    )

    lPainter.end()
    return QIcon(lPixmap)
