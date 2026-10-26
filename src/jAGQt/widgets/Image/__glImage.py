# ==================================================================================
# src/jAGQt/widgets/Image/__glImage.py
# ==================================================================================
from typing import Optional, Union

# ==================================================================================
from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QResizeEvent
from PySide6.QtOpenGLWidgets import QOpenGLWidget

# ==================================================================================
from ..components import ComponentBase
from .__fitMode import ImageFitMode
from .__imageBase import ImageBase


# ==================================================================================
class GLImage(QOpenGLWidget, ComponentBase, ImageBase):
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
        self._initImageBase(bg=bg, fitMode=fitMode)
        self._drawImage: Optional[QImage] = None
        self.setupUI()

    # ------------------------------------------------------------------
    def setupUI(self) -> None:
        self.setBackgroundColor(self._backgroundColor)

    # ------------------------------------------------------------------
    def _onImageCleared(self) -> None:
        self._drawImage = None
        self._drawRect = QRect()

    # ------------------------------------------------------------------
    def _recompute(self) -> None:
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
            self._drawRect = QRect((w - tw) // 2, (h - th) // 2, tw, th)
            return

        # Crop
        scale = max(w / iw, h / ih)
        tw = max(1, int(iw * scale))
        th = max(1, int(ih * scale))
        scaled = src.scaled(
            tw, th,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._drawImage = scaled.copy((tw - w) // 2, (th - h) // 2, w, h)
        self._drawRect = QRect(0, 0, w, h)

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
