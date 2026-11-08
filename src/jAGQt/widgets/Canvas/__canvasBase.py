# ==================================================================================
from __future__ import annotations

# ==================================================================================
import os
from typing import Optional, Tuple, Union

# ==================================================================================
from PySide6.QtCore import QPointF, QRect
from PySide6.QtGui import QColor, QImage, QPixmap

# ==================================================================================
from ...types.__eFitMode import CanvasFitMode

# ==================================================================================
BACKGROUND_COLOR = QColor("lightgray")
# ==================================================================================

# ==================================================================================
class CanvasBase:
    """
    Shared non-paint state for Canvas and GLCanvas.

    Fit geometry, content size, dirty flag, static image storage, and clear hooks.
    Input signals and paint live on the concrete QWidget / QOpenGLWidget subclasses.
    """

    def _wInitializeBase(self) -> None:
        self._image: Optional[QPixmap] = None
        self._drawRect: QRect = QRect()
        self._dirty: bool = True
        self._contentW: int = 0
        self._contentH: int = 0
        bg: Union[str, QColor] = self._backgroundColor
        self.setBackgroundColor(bg)

    @property
    def fitMode(self) -> CanvasFitMode:
        return self._fitMode

    @fitMode.setter
    def fitMode(self, value: CanvasFitMode) -> None:
        if value is self._fitMode: return
        self._fitMode = value
        self._markDirty()

    @property
    def image(self) -> Optional[QPixmap]:
        return self._image

    @image.setter
    def image(self, value: Union[QPixmap, QImage, str, None]) -> None:
        if value is None:
            self._image = None
            self._onImageCleared()
            self._markDirty()
            return

        pixmap = self._toPixmap(value)
        if pixmap is None or pixmap.isNull():
            return

        self._image = pixmap.copy()
        self._contentW = self._image.width()
        self._contentH = self._image.height()
        self._onImageSet()
        self._markDirty()

    # ------------------------------------------------------------------
    def setBackgroundColor(self, color: Union[str, QColor]) -> None:
        self._backgroundColor = QColor(color) if isinstance(color, str) else color
        self.update()

    def contentSize(self) -> Tuple[int, int]:
        if self._contentW > 0 and self._contentH > 0:
            return self._contentW, self._contentH
        src = self._sourceImage()
        if src is None:
            return 0, 0
        return src.width(), src.height()

    def fittedRect(self) -> QRect:
        vw = self.width()
        vh = self.height()
        iw, ih = self.contentSize()
        return self._fitRect(vw, vh, iw, ih)

    def mapToContent(self, x: float, y: float) -> Optional[Tuple[float, float]]:
        vw = self.width()
        vh = self.height()
        iw, ih = self.contentSize()
        if vw <= 0 or vh <= 0 or iw <= 0 or ih <= 0:
            return None

        mode = self._fitMode

        if mode is CanvasFitMode.Fill:
            return (x / vw) * iw, (y / vh) * ih

        if mode is CanvasFitMode.Scale:
            rect = self._fitRect(vw, vh, iw, ih)
            if rect.isEmpty():
                return None
            if not (
                rect.left() <= x < rect.left() + rect.width()
                and rect.top() <= y < rect.top() + rect.height()
            ):
                return None
            localX = (x - rect.left()) / max(1, rect.width())
            localY = (y - rect.top()) / max(1, rect.height())
            return localX * iw, localY * ih

        scale = max(vw / iw, vh / ih)
        tw = max(1.0, iw * scale)
        th = max(1.0, ih * scale)
        ox = (tw - vw) / 2.0
        oy = (th - vh) / 2.0
        return (x + ox) / scale, (y + oy) / scale

    def mapToContentPoint(self, pos: QPointF) -> Optional[QPointF]:
        mapped = self.mapToContent(float(pos.x()), float(pos.y()))
        if mapped is None:
            return None
        return QPointF(mapped[0], mapped[1])

    def clear(self) -> None:
        """Drop static and live content (iFrameView.clear)."""
        self._image = None
        self._contentW = 0
        self._contentH = 0
        self._onImageCleared()
        self._markDirty()

    # ------------------------------------------------------------------
    # HOOKS
    # ------------------------------------------------------------------
    def _onImageCleared(self) -> None:
        self._drawRect = QRect()

    def _onImageSet(self) -> None:
        pass

    def _markDirty(self) -> None:
        self._dirty = True
        self.update()  # type: ignore[attr-defined]

    def _sourceImage(self) -> Optional[QImage]:
        if self._image is not None and not self._image.isNull():
            return self._image.toImage()
        return None

    def _fitRect(self, vw: int, vh: int, iw: int, ih: int) -> QRect:
        if vw <= 0 or vh <= 0 or iw <= 0 or ih <= 0:
            return QRect()
        mode = self._fitMode
        if mode is CanvasFitMode.Fill:
            return QRect(0, 0, vw, vh)
        if mode is CanvasFitMode.Scale:
            scale = min(vw / iw, vh / ih)
            tw = max(1, int(iw * scale))
            th = max(1, int(ih * scale))
            return QRect((vw - tw) // 2, (vh - th) // 2, tw, th)
        return QRect(0, 0, vw, vh)

    @staticmethod
    def _toPixmap(value: Union[QPixmap, QImage, str]) -> Optional[QPixmap]:
        if isinstance(value, str):
            if not os.path.exists(value):
                return None
            return QPixmap(value)
        if isinstance(value, QImage):
            return QPixmap.fromImage(value)
        if isinstance(value, QPixmap):
            return value
        raise TypeError("Expected str | QImage | QPixmap | None")


# ==================================================================================
__all__ = ["CanvasBase", "BACKGROUND_COLOR"]
# ==================================================================================
