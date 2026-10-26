# ==================================================================================
# src/jAGQt/widgets/Image/__image.py
# ==================================================================================
import os
from typing import Optional, Union

# ==================================================================================
from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPaintEvent, QPixmap, QResizeEvent
from PySide6.QtWidgets import QWidget

# ==================================================================================
from ..components import ComponentBase
from .__fitMode import ImageFitMode


# ==================================================================================
class Image(QWidget, ComponentBase):
    """Software image display.

    Displays an image. Handles resize via ``fitMode``:

    - Scale — scale proportionally to fit inside the widget.
    - Fill  — stretch to fill the entire widget (aspect ignored).
    - Crop  — scale proportionally to cover, center, crop to viewport.
    """

    # ------------------------------------------------------------------
    def __init__(
        self,
        bg: Union[str, QColor] = "lightgray",
        fitMode: ImageFitMode = ImageFitMode.Scale,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self._image: Optional[QPixmap] = None
        self._backgroundColor: QColor = QColor(bg) if isinstance(bg, str) else bg
        self._fitMode: ImageFitMode = fitMode
        self._scaled: Optional[QPixmap] = None
        self._drawRect: QRect = QRect()
        self._dirty: bool = True

        self.setupUI()

    # ------------------------------------------------------------------
    def setupUI(self) -> None:
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setBackgroundColor(self._backgroundColor)

    # ------------------------------------------------------------------
    # PROPERTIES
    # ------------------------------------------------------------------
    @property
    def fitMode(self) -> ImageFitMode:
        return self._fitMode

    @fitMode.setter
    def fitMode(self, value: ImageFitMode) -> None:
        if value is self._fitMode:
            return
        self._fitMode = value
        self._dirty = True
        self.update()

    @property
    def image(self) -> Optional[QPixmap]:
        return self._image

    @image.setter
    def image(self, value: Union[QPixmap, QImage, str, None]) -> None:
        if value is None:
            self._image = None
            self._scaled = None
            self._drawRect = QRect()
            self._dirty = True
            self.update()
            return

        lPixmap: Optional[QPixmap] = None

        if isinstance(value, str):
            if not os.path.exists(value):
                return
            lPixmap = QPixmap(value)
        elif isinstance(value, QImage):
            lPixmap = QPixmap.fromImage(value)
        elif isinstance(value, QPixmap):
            lPixmap = value
        else:
            raise TypeError("Expected str | QImage | QPixmap | None")

        if lPixmap is None or lPixmap.isNull():
            return

        self._image = lPixmap.copy()
        self._dirty = True
        self.update()

    # ------------------------------------------------------------------
    def setBackgroundColor(self, color: Union[str, QColor]) -> None:
        self._backgroundColor = QColor(color) if isinstance(color, str) else color
        self.update()

    # ------------------------------------------------------------------
    # LAYOUT
    # ------------------------------------------------------------------
    def _recompute(self) -> None:
        """Recompute scaled pixmap and draw rect from current size and fitMode."""
        self._dirty = False
        self._scaled = None
        self._drawRect = QRect()

        if self._image is None or self._image.isNull():
            return

        w = self.width()
        h = self.height()
        if w <= 0 or h <= 0:
            return

        iw = self._image.width()
        ih = self._image.height()
        if iw <= 0 or ih <= 0:
            return

        mode = self._fitMode

        if mode is ImageFitMode.Fill:
            self._scaled = self._image.scaled(
                w, h,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self._drawRect = QRect(0, 0, w, h)
            return

        if mode is ImageFitMode.Scale:
            scale = min(w / iw, h / ih)
            tw = max(1, int(iw * scale))
            th = max(1, int(ih * scale))
            self._scaled = self._image.scaled(
                tw, th,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            x = (w - tw) // 2
            y = (h - th) // 2
            self._drawRect = QRect(x, y, tw, th)
            return

        # Crop — cover, keep aspect, center crop.
        scale = max(w / iw, h / ih)
        tw = max(1, int(iw * scale))
        th = max(1, int(ih * scale))
        scaled = self._image.scaled(
            tw, th,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        x = (tw - w) // 2
        y = (th - h) // 2
        self._scaled = scaled.copy(x, y, w, h)
        self._drawRect = QRect(0, 0, w, h)

    # ------------------------------------------------------------------
    # EVENTS (resize + paint only)
    # ------------------------------------------------------------------
    def resizeEvent(self, event: QResizeEvent) -> None:
        self._dirty = True
        super().resizeEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        if self._dirty:
            self._recompute()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.fillRect(self.rect(), self._backgroundColor)

        if self._scaled is not None and not self._scaled.isNull() and not self._drawRect.isEmpty():
            painter.drawPixmap(self._drawRect, self._scaled)

        painter.end()
