# ==================================================================================
from typing import Optional, Union

# ==================================================================================
from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QResizeEvent
from PySide6.QtOpenGLWidgets import QOpenGLWidget

# ==================================================================================
from jAGFx.workflow import workflow

# ==================================================================================
from ..components import ComponentBase
from .__fitMode import ImageFitMode
from .__imageBase import BACKGROUND_COLOR, ImageBase


# ==================================================================================
@workflow("InitializeBase")
class GLImage(QOpenGLWidget, ComponentBase, ImageBase):
    def __init__(
        self, bg: Union[str, QColor] = BACKGROUND_COLOR,
        fitMode: ImageFitMode = ImageFitMode.Scale,
        *args, **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._backgroundColor = QColor(bg) if isinstance(bg, str) else bg
        self._fitMode: ImageFitMode = fitMode
        self._drawImage: Optional[QImage] = None
        self._glIntialized: bool = False

    def _initializeGL(self) -> None:
        self.gl = self.context().functions()
        self.gl.glClearColor(
            self._backgroundColor.redF(),
            self._backgroundColor.greenF(),
            self._backgroundColor.blueF(),
            1.0,
        )

    def _onImageCleared(self) -> None:
        self._drawImage = None
        self._drawRect = QRect()

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

    def resizeGL(self, w: int, h: int) -> None:
        if not self._glIntialized: self._initializeGL()
        if hasattr(self, "gl") and self.gl is not None:
            self.gl.glViewport(0, 0, w, h)
        self._dirty = True

    def resizeEvent(self, event: QResizeEvent) -> None:
        self._dirty = True
        super().resizeEvent(event)

    def paintGL(self) -> None:
        if not self._glIntialized: self._initializeGL()

        if self._dirty: self._recompute()

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
