# ==================================================================================
# src/jAGQt/animations/wipe/__wipeAnimationBase.py
# ==================================================================================
from __future__ import annotations

# ==================================================================================
import math
from typing import Optional, Union

# ==================================================================================
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import QLabel, QWidget

# ==================================================================================
from jAGQt.utilities import AnimationError

# ==================================================================================
from ..__animationBase import AnimationBase
from .__eWipeMode import eWipeMode

# ==================================================================================
C_BLADE_WIDTH = 3
C_BLADE_COLOR = QColor(220, 220, 230, 230)
ImageLike = Union[QPixmap, QImage, str]
# ==================================================================================


# ==================================================================================
def _toPixmap(source: Optional[ImageLike], sizeHint: QPixmap | None = None) -> QPixmap:
    if source is None:
        return QPixmap()
    if isinstance(source, QPixmap):
        return source
    if isinstance(source, QImage):
        return QPixmap.fromImage(source)
    if isinstance(source, str):
        px = QPixmap(source)
        if px.isNull():
            raise AnimationError(f"Failed to load image from path: {source!r}")
        return px
    raise AnimationError(f"Unsupported image type: {type(source).__name__}")


# ==================================================================================
class WipeAnimationBase(AnimationBase):
    """Shared wipe geometry; paint strategy is grab + setPixmap on the target."""

    def __init__(
        self,
        target: QWidget,
        mode: eWipeMode = eWipeMode.Horizontal,
        bladeWidth: int = C_BLADE_WIDTH,
        bladeColor: Optional[QColor] = None,
        *args,
        **kwargs,
    ) -> None:
        if target is None:
            raise AnimationError("Wipe target must not be None")
        super().__init__(*args, **kwargs)
        self._target: QWidget = target
        self._mode: eWipeMode = mode
        self._bladeWidth: int = max(1, int(bladeWidth))
        self._bladeColor: QColor = bladeColor or QColor(C_BLADE_COLOR)
        self._original: QPixmap = QPixmap()
        self._content: QPixmap = QPixmap()
        self._frameSize = target.size()

    @property
    def mode(self) -> eWipeMode:
        return self._mode

    @mode.setter
    def mode(self, value: eWipeMode) -> None:
        self._mode = value

    def _grabTarget(self) -> QPixmap:
        grab = self._target.grab()
        if grab.isNull():
            w = max(1, self._target.width())
            h = max(1, self._target.height())
            grab = QPixmap(w, h)
            grab.fill(Qt.GlobalColor.transparent)
        return grab

    def _applyPixmap(self, pixmap: QPixmap) -> None:
        target = self._target
        if isinstance(target, QLabel):
            target.setPixmap(pixmap)
            return
        setPixmap = getattr(target, "setPixmap", None)
        if callable(setPixmap):
            setPixmap(pixmap)
            return
        raise AnimationError(
            f"Target {type(target).__name__} does not support setPixmap; use QLabel-based widgets"
        )

    def _scaled(self, pixmap: QPixmap) -> QPixmap:
        if pixmap.isNull():
            return pixmap
        size = self._target.size()
        if size.width() <= 0 or size.height() <= 0:
            return pixmap
        return pixmap.scaled(
            size,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

    def _buildFrame(
        self,
        progress: float,
        underneath: QPixmap,
        revealed: QPixmap,
    ) -> QPixmap:
        """Composite *revealed* into the wiped region over *underneath*; draw blade."""
        progress = max(0.0, min(1.0, progress))
        w = max(1, self._target.width())
        h = max(1, self._target.height())
        frame = QPixmap(w, h)
        frame.fill(Qt.GlobalColor.transparent)

        under = self._scaled(underneath) if not underneath.isNull() else QPixmap()
        over = self._scaled(revealed) if not revealed.isNull() else QPixmap()

        painter = QPainter(frame)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        if not under.isNull():
            painter.drawPixmap(0, 0, under)

        path = self._wipedRegionPath(w, h, progress)
        if not path.isEmpty():
            painter.save()
            painter.setClipPath(path)
            if not over.isNull():
                painter.drawPixmap(0, 0, over)
            else:
                painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
                painter.fillRect(frame.rect(), Qt.GlobalColor.transparent)
            painter.restore()

        self._drawBlade(painter, w, h, progress)
        painter.end()
        return frame

    def _wipedRegionPath(self, w: int, h: int, progress: float) -> QPainterPath:
        path = QPainterPath()
        if progress <= 0.0:
            return path
        if progress >= 1.0:
            path.addRect(QRectF(0, 0, w, h))
            return path

        if self._mode is eWipeMode.Horizontal:
            path.addRect(QRectF(0, 0, w * progress, h))
        elif self._mode is eWipeMode.Vertical:
            path.addRect(QRectF(0, 0, w, h * progress))
        else:
            pivot = QPointF(w * 0.5, h * 1.05)
            radius = (w * w + h * h) ** 0.5
            startAngle = 180.0
            span = -180.0 * progress
            path.moveTo(pivot)
            path.arcTo(
                pivot.x() - radius,
                pivot.y() - radius,
                radius * 2,
                radius * 2,
                startAngle,
                span,
            )
            path.closeSubpath()
        return path

    def _drawBlade(self, painter: QPainter, w: int, h: int, progress: float) -> None:
        if progress <= 0.0 or progress >= 1.0:
            return
        pen = QPen(self._bladeColor)
        pen.setWidth(self._bladeWidth)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        if self._mode is eWipeMode.Horizontal:
            x = w * progress
            painter.drawLine(QPointF(x, 0), QPointF(x, h))
        elif self._mode is eWipeMode.Vertical:
            y = h * progress
            painter.drawLine(QPointF(0, y), QPointF(w, y))
        else:
            pivot = QPointF(w * 0.5, h * 1.05)
            radius = (w * w + h * h) ** 0.5
            angleRad = math.radians(180.0 - 180.0 * progress)
            end = QPointF(
                pivot.x() + radius * math.cos(angleRad),
                pivot.y() - radius * math.sin(angleRad),
            )
            painter.drawLine(pivot, end)
