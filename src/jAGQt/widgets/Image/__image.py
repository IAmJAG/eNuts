# ==================================================================================
# src/jAGQt/widgets/Image/__image.py
# ==================================================================================
import os
from typing import Literal, Optional, Union

# ==================================================================================
from PySide6.QtCore import QPoint, QPointF, QSize, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QImage,
    QMouseEvent,
    QPainter,
    QPaintEvent,
    QPixmap,
    QResizeEvent,
    QWheelEvent,
)
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtOpenGL import QOpenGLTexture
from PySide6.QtWidgets import QWidget
from torch import Tensor

# ==================================================================================
from jAGQt.types.components import ComponentBase


# ==================================================================================
Backend = Literal["software", "opengl"]


# ==================================================================================
class Image(QWidget, ComponentBase):
    """Fast image viewer with zoom / pan.

    backend="software"  → pure QWidget + cached scaled QPixmap (default)
    backend="opengl"    → QOpenGLWidget child (GPU-backed)
    """

    onResize: Signal = Signal(QSize)
    onZoomChanged: Signal = Signal(float)

    # ------------------------------------------------------------------
    def __init__(
        self,
        bg: Union[str, QColor] = "lightgray",
        backend: Backend = "software",
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self._backend: Backend = backend
        self._image: Optional[QPixmap] = None
        self._zoom: float = 100.0
        self._offset: QPointF = QPointF(0.0, 0.0)
        self._backgroundColor: QColor = QColor(bg) if isinstance(bg, str) else bg

        # software path state
        self._scaled: Optional[QPixmap] = None
        self._dirty: bool = True

        # shared interaction state
        self._lastMousePos: Optional[QPoint] = None
        self._panning: bool = False

        # OpenGL child (created only when needed)
        self._gl: Optional["_GLView"] = None

        self.setupUI()

    # ------------------------------------------------------------------
    def setupUI(self) -> None:
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setBackgroundColor(self._backgroundColor)

        if self._backend == "opengl":
            self._gl = _GLView(self)
            self._gl.setGeometry(self.rect())
            self._gl.show()

    # ------------------------------------------------------------------
    # PROPERTIES
    # ------------------------------------------------------------------
    @property
    def backend(self) -> Backend:
        return self._backend

    @property
    def zoom(self) -> float:
        return self._zoom

    @zoom.setter
    def zoom(self, value: float) -> None:
        lNew = max(1.0, min(value, 10_000.0))
        if abs(lNew - self._zoom) < 0.01:
            return
        self._zoom = lNew
        self._dirty = True
        self.onZoomChanged.emit(self._zoom)
        self._requestUpdate()

    @property
    def offset(self) -> QPointF:
        return self._offset

    @offset.setter
    def offset(self, value: Union[QPoint, QPointF]) -> None:
        if isinstance(value, QPoint):
            value = QPointF(value)
        if value == self._offset:
            return
        self._offset = value
        self._requestUpdate()

    @property
    def image(self) -> Optional[QPixmap]:
        return self._image

    @image.setter
    def image(self, value: Union[QPixmap, QImage, str, Tensor, None]) -> None:
        if value is None:
            self._image = None
            self._scaled = None
            self._dirty = True
            self.resetView()
            self._requestUpdate()
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
        self.resetView()
        self._requestUpdate()

        if self._gl is not None:
            self._gl.setImage(self._image)

    # ------------------------------------------------------------------
    def setBackgroundColor(self, color: Union[str, QColor]) -> None:
        self._backgroundColor = QColor(color) if isinstance(color, str) else color
        if self._gl is not None:
            self._gl.setBackgroundColor(self._backgroundColor)
        self._requestUpdate()

    # ------------------------------------------------------------------
    # LOGIC
    # ------------------------------------------------------------------
    def resetView(self) -> None:
        if self._image is None or self._image.isNull() or self.width() <= 0 or self.height() <= 0:
            self._zoom = 100.0
            self._offset = QPointF(0.0, 0.0)
            self._dirty = True
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
        self._dirty = True
        self.onZoomChanged.emit(self._zoom)

        if self._gl is not None:
            self._gl.setTransform(self._zoom, self._offset)

    def _rebuildScaled(self) -> None:
        if self._image is None or self._image.isNull():
            self._scaled = None
            self._dirty = False
            return

        lScale = self._zoom / 100.0
        lTarget = QSize(
            max(1, int(self._image.width() * lScale)),
            max(1, int(self._image.height() * lScale)),
        )
        self._scaled = self._image.scaled(
            lTarget,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._dirty = False

    def _requestUpdate(self) -> None:
        if self._gl is not None:
            self._gl.setTransform(self._zoom, self._offset)
            self._gl.update()
        else:
            self.update()

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
    # EVENTS
    # ------------------------------------------------------------------
    def resizeEvent(self, event: QResizeEvent) -> None:
        self.onResize.emit(event.size())
        if self._gl is not None:
            self._gl.setGeometry(self.rect())
        super().resizeEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        if self._backend == "opengl":
            return  # child does the work

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.fillRect(self.rect(), self._backgroundColor)

        if self._image is None or self._image.isNull():
            painter.end()
            return

        if self._dirty or self._scaled is None:
            self._rebuildScaled()

        if self._scaled is not None and not self._scaled.isNull():
            painter.drawPixmap(self._offset.toPoint(), self._scaled)

        painter.end()

    def wheelEvent(self, event: QWheelEvent) -> None:
        if self._image is None:
            return

        lDelta = event.angleDelta().y()
        lFactor = 1.15 if lDelta > 0 else 1.0 / 1.15
        lOldZoom = self._zoom
        self.zoom = self._zoom * lFactor

        lPos = event.position()
        lRatio = self._zoom / lOldZoom
        self._offset = lPos - (lPos - self._offset) * lRatio
        self._requestUpdate()
        event.accept()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._panning = True
            self._lastMousePos = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._panning and self._lastMousePos is not None:
            lDelta = event.position().toPoint() - self._lastMousePos
            self._offset += QPointF(lDelta)
            self._lastMousePos = event.position().toPoint()
            self._requestUpdate()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self._panning:
            self._panning = False
            self._lastMousePos = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        self.resetView()
        self._requestUpdate()
        event.accept()


# ==================================================================================
# OpenGL renderer (private)
# ==================================================================================
class _GLView(QOpenGLWidget):
    """GPU-backed view used when Image(backend="opengl").

    Uses QPainter over the GL context for maximum cross-platform reliability
    with pure PySide6 (no fixed-function pipeline / no PyOpenGL dependency).
    """

    def __init__(self, parent: Image) -> None:
        super().__init__(parent)
        self._owner = parent
        self._texture: Optional[QOpenGLTexture] = None
        self._imageFallback: Optional[QImage] = None
        self._bg = QColor("lightgray")
        self._zoom = 100.0
        self._offset = QPointF(0.0, 0.0)
        self._imgW = 0
        self._imgH = 0

    def setBackgroundColor(self, color: QColor) -> None:
        self._bg = color

    def setImage(self, pixmap: QPixmap) -> None:
        if pixmap is None or pixmap.isNull():
            self._imageFallback = None
            self._imgW = 0
            self._imgH = 0
            if self._texture is not None:
                self._texture.destroy()
                self._texture = None
            self.update()
            return

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
        self.update()

    def setTransform(self, zoom: float, offset: QPointF) -> None:
        self._zoom = zoom
        self._offset = offset

    def initializeGL(self) -> None:
        self.gl = self.context().functions()
        self.gl.glClearColor(
            self._bg.redF(), self._bg.greenF(), self._bg.blueF(), 1.0
        )

    def resizeGL(self, w: int, h: int) -> None:
        if hasattr(self, "gl") and self.gl is not None:
            self.gl.glViewport(0, 0, w, h)

    def paintGL(self) -> None:
        if hasattr(self, "gl") and self.gl is not None:
            self.gl.glClearColor(
                self._bg.redF(), self._bg.greenF(), self._bg.blueF(), 1.0
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
            w, h,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        painter.drawImage(QPointF(x, y), scaled)
        painter.end()
