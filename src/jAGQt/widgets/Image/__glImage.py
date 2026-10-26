# ==================================================================================
# src/jAGQt/widgets/Image/__glImage.py
# ==================================================================================
import os
from typing import Optional, Union

# ==================================================================================
from PySide6.QtCore import QPointF, QSize, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QImage,
    QPainter,
    QPixmap,
    QResizeEvent,
)
from PySide6.QtOpenGL import QOpenGLTexture
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from torch import Tensor

# ==================================================================================
from ..components import ComponentBase


# ==================================================================================
class GLImage(QOpenGLWidget, ComponentBase):
    """OpenGL image display. Display only — no pan, zoom, or mouse interaction.

    GPU-backed via QOpenGLWidget + QPainter over the GL context.
    """

    onResize: Signal = Signal(QSize)

    # ------------------------------------------------------------------
    def __init__(
        self,
        bg: Union[str, QColor] = "lightgray",
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self._image: Optional[QPixmap] = None
        self._zoom: float = 100.0
        self._offset: QPointF = QPointF(0.0, 0.0)
        self._backgroundColor: QColor = QColor(bg) if isinstance(bg, str) else bg

        self._texture: Optional[QOpenGLTexture] = None
        self._imageFallback: Optional[QImage] = None
        self._imgW: int = 0
        self._imgH: int = 0

        self.setupUI()

    # ------------------------------------------------------------------
    def setupUI(self) -> None:
        self.setBackgroundColor(self._backgroundColor)

    # ------------------------------------------------------------------
    # PROPERTIES
    # ------------------------------------------------------------------
    @property
    def zoom(self) -> float:
        return self._zoom

    @zoom.setter
    def zoom(self, value: float) -> None:
        lNew = max(1.0, min(value, 10_000.0))
        if abs(lNew - self._zoom) < 0.01:
            return
        self._zoom = lNew
        self.update()

    @property
    def offset(self) -> QPointF:
        return self._offset

    @offset.setter
    def offset(self, value: Union[QPointF, tuple]) -> None:
        if not isinstance(value, QPointF):
            value = QPointF(*value)
        if value == self._offset:
            return
        self._offset = value
        self.update()

    @property
    def image(self) -> Optional[QPixmap]:
        return self._image

    @image.setter
    def image(self, value: Union[QPixmap, QImage, str, Tensor, None]) -> None:
        if value is None:
            self._image = None
            self._clearTexture()
            self.resetView()
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
        self._uploadTexture(self._image)
        self.resetView()
        self.update()

    # ------------------------------------------------------------------
    def setBackgroundColor(self, color: Union[str, QColor]) -> None:
        self._backgroundColor = QColor(color) if isinstance(color, str) else color
        self.update()

    # ------------------------------------------------------------------
    # LOGIC
    # ------------------------------------------------------------------
    def resetView(self) -> None:
        """Fit image to widget (aspect-preserving) and center."""
        if self._image is None or self._image.isNull() or self.width() <= 0 or self.height() <= 0:
            self._zoom = 100.0
            self._offset = QPointF(0.0, 0.0)
            return

        lWRatio = self.width() / self._image.width()
        lHRatio = self.height() / self._image.height()
        lFit = min(lWRatio, lHRatio)

        self._zoom = lFit * 100.0
        lScaledW = self._image.width() * lFit
        lScaledH = self._image.height() * lFit
        self._offset = QPointF(
            (self.width() - lScaledW) * 0.5,
            (self.height() - lScaledH) * 0.5,
        )

    def _clearTexture(self) -> None:
        self._imageFallback = None
        self._imgW = 0
        self._imgH = 0
        if self._texture is not None:
            self._texture.destroy()
            self._texture = None

    def _uploadTexture(self, pixmap: QPixmap) -> None:
        qimg = pixmap.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        self._imgW = qimg.width()
        self._imgH = qimg.height()
        self._imageFallback = qimg

        if self._texture is not None:
            self._texture.destroy()

        self._texture = QOpenGLTexture(QOpenGLTexture.Target.Target2D)
        self._texture.setData(qimg)
        self._texture.setMinificationFilter(QOpenGLTexture.Filter.Linear)
        self._texture.setMagnificationFilter(QOpenGLTexture.Filter.Linear)
        self._texture.setWrapMode(QOpenGLTexture.WrapMode.ClampToEdge)

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
    # GL
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

    def paintGL(self) -> None:
        if hasattr(self, "gl") and self.gl is not None:
            self.gl.glClearColor(
                self._backgroundColor.redF(),
                self._backgroundColor.greenF(),
                self._backgroundColor.blueF(),
                1.0,
            )
            self.gl.glClear(0x00004000)  # GL_COLOR_BUFFER_BIT

        if self._imageFallback is None:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        scale = self._zoom / 100.0
        x = self._offset.x()
        y = self._offset.y()
        w = max(1, int(self._imgW * scale))
        h = max(1, int(self._imgH * scale))

        scaled = self._imageFallback.scaled(
            w,
            h,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        painter.drawImage(QPointF(x, y), scaled)
        painter.end()

    # ------------------------------------------------------------------
    # EVENTS
    # ------------------------------------------------------------------
    def resizeEvent(self, event: QResizeEvent) -> None:
        self.onResize.emit(event.size())
        if self._image is not None and not self._image.isNull():
            self.resetView()
        super().resizeEvent(event)
