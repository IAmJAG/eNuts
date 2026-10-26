# ==================================================================================
# src/jAGQt/widgets/Image/__image.py
# ==================================================================================
from typing import Optional, Union

# ==================================================================================
from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QPainter, QPaintEvent, QPixmap, QResizeEvent
from PySide6.QtWidgets import QWidget

# ==================================================================================
from ..components import ComponentBase
from .__fitMode import ImageFitMode
from .__imageBase import ImageBase


# ==================================================================================
class Image(QWidget, ComponentBase, ImageBase):
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
        self._initImageBase(bg=bg, fitMode=fitMode)
        self._scaled: Optional[QPixmap] = None
        self.setupUI()

    # ------------------------------------------------------------------
    def setupUI(self) -> None:
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setBackgroundColor(self._backgroundColor)

    # ------------------------------------------------------------------
    def _onImageCleared(self) -> None:
        self._scaled = None
        self._drawRect = QRect()

    # ------------------------------------------------------------------
    def _recompute(self) -> None:
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
            self._drawRect = QRect((w - tw) // 2, (h - th) // 2, tw, th)
            return

        # Crop
        scale = max(w / iw, h / ih)
        tw = max(1, int(iw * scale))
        th = max(1, int(ih * scale))
        scaled = self._image.scaled(
            tw, th,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._scaled = scaled.copy((tw - w) // 2, (th - h) // 2, w, h)
        self._drawRect = QRect(0, 0, w, h)

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
