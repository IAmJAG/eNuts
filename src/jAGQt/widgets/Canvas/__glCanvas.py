# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional, Union

# ==================================================================================
from PySide6.QtCore import QRect, QSize, Qt, Signal, SignalInstance
from PySide6.QtGui import (
    QColor,
    QFocusEvent,
    QImage,
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QPixmap,
    QResizeEvent,
)
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QSizePolicy
from torch import Tensor

# ==================================================================================
from jAGFx.workflow import workflow

# ==================================================================================
from ...types import eCanvasFitMode
from ..components import ComponentBase
from .__canvasBase import BACKGROUND_COLOR, CanvasBase


# ==================================================================================
@workflow("InitializeBase")
class GLCanvas(QOpenGLWidget, ComponentBase, CanvasBase):
    """OpenGL canvas: live present(Tensor|Handle|QImage) + static image + input signals.

    Until GPU interop exists, Tensor frames are converted to QImage inside the view.
    """

    keyPressed: SignalInstance = Signal(object)
    keyReleased: SignalInstance = Signal(object)
    mousePressed: SignalInstance = Signal(object)
    mouseMoved: SignalInstance = Signal(object)
    mouseReleased: SignalInstance = Signal(object)

    def __init__(
        self,
        bg: Union[str, QColor] = BACKGROUND_COLOR,
        fitMode: eCanvasFitMode = eCanvasFitMode.Scale,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._backgroundColor = QColor(bg) if isinstance(bg, str) else bg
        self._fitMode: eCanvasFitMode = fitMode
        self._drawImage: Optional[QImage] = None
        self._glIntialized: bool = False
        self._liveImage: Optional[QImage] = None

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(1, 1)

    def sizeHint(self) -> QSize:
        return QSize(640, 480)

    def minimumSizeHint(self) -> QSize:
        return QSize(320, 240)

    # ------------------------------------------------------------------
    # iFrameView
    # ------------------------------------------------------------------
    def present(self, frame: Tensor | object) -> bool:
        if isinstance(frame, QImage):
            image = frame if not frame.isNull() else None
        elif isinstance(frame, QPixmap):
            image = frame.toImage() if not frame.isNull() else None
        elif isinstance(frame, Tensor):
            image = self._tensorToQImage(frame)
        else:
            # Future: GPU handle interop — not implemented yet.
            self._liveImage = None
            self._dirty = True
            self.update()
            return True

        if image is None or image.isNull():
            return False

        self._liveImage = image.copy()
        self._contentW = self._liveImage.width()
        self._contentH = self._liveImage.height()
        self._dirty = True
        self.update()
        return True

    def clear(self) -> None:
        self._liveImage = None
        self._drawImage = None
        super().clear()

    @staticmethod
    def _tensorToQImage(frame: Tensor) -> Optional[QImage]:
        try:
            t = frame.detach()
            if t.is_cuda:
                t = t.cpu()
            arr = t.numpy()
            if arr.ndim == 3 and arr.shape[-1] == 3:
                h, w, _ = arr.shape
                if not arr.flags["C_CONTIGUOUS"]:
                    arr = arr.copy()
                return QImage(arr.data, w, h, 3 * w, QImage.Format.Format_RGB888).copy()
        except Exception as ex:
            warning(f"[GLCanvas] Tensor→QImage failed: {ex}")
        return None

    def _sourceImage(self) -> Optional[QImage]:
        if self._liveImage is not None and not self._liveImage.isNull():
            return self._liveImage
        return super()._sourceImage()

    def _onImageCleared(self) -> None:
        self._drawImage = None
        self._drawRect = QRect()

    def _recompute(self) -> None:
        self._dirty = False
        self._drawImage = None
        self._drawRect = QRect()

        src = self._sourceImage()
        if src is None or src.isNull():
            return

        w = self.width()
        h = self.height()
        iw, ih = self.contentSize()
        if iw <= 0 or ih <= 0:
            iw, ih = src.width(), src.height()
        if w <= 0 or h <= 0 or iw <= 0 or ih <= 0:
            return

        self._drawRect = self._fitRect(w, h, iw, ih)
        mode = self._fitMode

        if mode is eCanvasFitMode.Fill:
            self._drawImage = src.scaled(
                w, h,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.FastTransformation,
            )
            return

        if mode is eCanvasFitMode.Scale:
            self._drawImage = src.scaled(
                self._drawRect.size(),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.FastTransformation,
            )
            return

        scale = max(w / iw, h / ih)
        tw = max(1, int(iw * scale))
        th = max(1, int(ih * scale))
        scaled = src.scaled(
            tw, th,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation,
        )
        self._drawImage = scaled.copy((tw - w) // 2, (th - h) // 2, w, h)

    def _initializeGL(self) -> None:
        self.gl = self.context().functions()
        self.gl.glClearColor(
            self._backgroundColor.redF(),
            self._backgroundColor.greenF(),
            self._backgroundColor.blueF(),
            1.0,
        )
        self._glIntialized = True

    def resizeGL(self, w: int, h: int) -> None:
        if not self._glIntialized:
            self._initializeGL()
        if hasattr(self, "gl") and self.gl is not None:
            self.gl.glViewport(0, 0, w, h)
        self._dirty = True

    def resizeEvent(self, event: QResizeEvent) -> None:
        self._dirty = True
        super().resizeEvent(event)

    def paintGL(self) -> None:
        if not self._glIntialized:
            self._initializeGL()

        if self._dirty:
            self._recompute()

        if hasattr(self, "gl") and self.gl is not None:
            self.gl.glClearColor(
                self._backgroundColor.redF(),
                self._backgroundColor.greenF(),
                self._backgroundColor.blueF(),
                1.0,
            )
            self.gl.glClear(0x00004000)

        if self._drawImage is None or self._drawRect.isEmpty():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
        painter.drawImage(self._drawRect, self._drawImage)
        painter.end()

    def focusInEvent(self, event: QFocusEvent) -> None:
        super().focusInEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        self.keyPressed.emit(event)
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        self.keyReleased.emit(event)
        super().keyReleaseEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if not self.hasFocus():
            self.setFocus(Qt.FocusReason.MouseFocusReason)
        self.mousePressed.emit(event)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self.mouseMoved.emit(event)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.mouseReleased.emit(event)
        super().mouseReleaseEvent(event)


# ==================================================================================
__all__ = ["GLCanvas"]
# ==================================================================================
