# ==================================================================================
# src/jAGQt/widgets/Image/__glImage.py
# ==================================================================================
import os
from typing import Optional, Union

# ==================================================================================
from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPixmap, QResizeEvent
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from torch import Tensor

# ==================================================================================
from ..components import ComponentBase
from .__fitMode import ImageFitMode


# ==================================================================================
class GLImage(QOpenGLWidget, ComponentBase):
    """OpenGL image display.

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
        self._drawImage: Optional[QImage] = None
        self._drawRect: QRect = QRect()
        self._dirty: bool = True

        self.setupUI()

    # ------------------------------------------------------------------
    def setupUI(self) -> None:
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
    def image(self, value: Union[QPixmap, QImage, str, Tensor, None]) -> None:
        if value is None:
            self._image = None
            self._drawImage = None
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
        elif isinstance(value, Tensor):
            lPixmap = self._tensorToPixmap(value)
        else:
            raise TypeError("Expected str | QImage | QPixmap | Tensor | None")

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
        """Recompute draw image and rect from current size and fitMode."""
        self._dirty = False
        self._drawImage = None
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

        src = self._image.toImage()
        mode = self._fitMode

        if mode is ImageFitMode.Fill:
            self._drawImage = src.scaled(
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
            self._drawImage = src.scaled(
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
        scaled = src.scaled(
            tw, th,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        x = (tw - w) // 2
        y = (th - h) // 2
        self._drawImage = scaled.copy(x, y, w, h)
        self._drawRect = QRect(0, 0, w, h)

    @staticmethod
    def _tensorToPixmap(tensor: Tensor) -> QPixmap:
        t = tensor.detach().cpu()
        if t.ndim == 4:
            t = t[0]
        if t.ndim == 3 and t.shape[0] in (1, 3, 4):
            t = t.permute(1, 2, 0)
        if t.dtype.is_floating_point:
            t = (t.clamp(0, 1) * 255).to("uint8")
        else:
            t = t.to("uint8")

        h, w, c = t.shape
        if c == 1:
            fmt = QImage.Format.Format_Grayscale8
        elif c == 3:
            fmt = QImage.Format.Format_RGB888
        elif c == 4:
            fmt = QImage.Format.Format_RGBA8888
        else:
            raise ValueError(f"Unsupported channel count: {c}")

        t = t.contiguous()
        qimg = QImage(t.data_ptr(), w, h, t.stride(0), fmt).copy()
        return QPixmap.fromImage(qimg)

    # ------------------------------------------------------------------
    # GL (paint only) + resize
    # ------------------------------------------------------------------
    def initializeGL(self) -> None:
        self.gl = self.context().functions()
        self.gl.glClearColor(
            self._backgroundColor.redF(),
            self._backgroundColor.greenF(),
            self._backgroundColor.blueF(),
            1.0,
        )

    def resizeGL(self, w: int, h: int) -> None:
        if hasattr(self, "gl") and self.gl is not None:
            self.gl.glViewport(0, 0, w, h)
        self._dirty = True

    def resizeEvent(self, event: QResizeEvent) -> None:
        self._dirty = True
        super().resizeEvent(event)

    def paintGL(self) -> None:
        if self._dirty:
            self._recompute()

        if hasattr(self, "gl") and self.gl is not None:
            self.gl.glClearColor(
                self._backgroundColor.redF(),
                self._backgroundColor.greenF(),
                self._backgroundColor.blueF(),
                1.0,
            )
            self.gl.glClear(0x00004000)  # GL_COLOR_BUFFER_BIT

        if self._drawImage is None or self._drawRect.isEmpty():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.drawImage(self._drawRect, self._drawImage)
        painter.end()
