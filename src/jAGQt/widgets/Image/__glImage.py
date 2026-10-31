# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional, Union

# ==================================================================================
from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QResizeEvent
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QSizePolicy

# ==================================================================================
from jAGFx.workflow import workflow

# ==================================================================================
from ..components import ComponentBase
from .__fitMode import ImageFitMode
from .__imageBase import BACKGROUND_COLOR, ImageBase


# ==================================================================================
@workflow("InitializeBase")
class GLImage(QOpenGLWidget, ComponentBase, ImageBase):
    """OpenGL image view.

    Static path: ``image`` setter (QPixmap/QImage).
    Live path: ``presentExternal`` — stream frames. Fit uses content size vs widget
    size (Scale/Fill/Crop). Resize refits without a new producer frame.

    ``handle`` is reserved for GPU interop; until the platform importer exists,
    pass a decoded ``QImage`` on the transitional path.
    """

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

        self._liveSeq: int | None = None
        self._livePts: int = 0
        self._contentW: int = 0
        self._contentH: int = 0
        self._liveImage: Optional[QImage] = None

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(1, 1)

    def sizeHint(self) -> QSize:
        # Prefer filling the layout; QOpenGLWidget default hint is often tiny.
        return QSize(640, 480)

    def minimumSizeHint(self) -> QSize:
        return QSize(320, 240)

    def presentExternal(
        self,
        *,
        seq: int,
        width: int,
        height: int,
        pts: int = 0,
        image: QImage | None = None,
        handle: object | None = None,
    ) -> bool:
        """Present a stream frame. Returns False if skipped (same seq)."""
        if self._liveSeq is not None and int(seq) == self._liveSeq:
            return False

        self._liveSeq = int(seq)
        self._livePts = int(pts)
        self._contentW = max(0, int(width))
        self._contentH = max(0, int(height))

        if handle is not None and image is None:
            # GPU interop import not implemented yet — cannot present handle-only.
            self._liveImage = None
            self._dirty = True
            self.update()
            return True

        if image is not None and not image.isNull():
            self._liveImage = image.copy()
            if self._contentW <= 0:
                self._contentW = self._liveImage.width()
            if self._contentH <= 0:
                self._contentH = self._liveImage.height()
        else:
            self._liveImage = None

        self._dirty = True
        self.update()
        return True

    def clearPresent(self) -> None:
        self._liveSeq = None
        self._livePts = 0
        self._contentW = 0
        self._contentH = 0
        self._liveImage = None
        self._drawImage = None
        self._drawRect = QRect()
        self._dirty = True
        self.update()

    @property
    def liveSeq(self) -> int | None:
        return self._liveSeq

    @property
    def livePts(self) -> int:
        return self._livePts

    def _initializeGL(self) -> None:
        self.gl = self.context().functions()
        self.gl.glClearColor(
            self._backgroundColor.redF(),
            self._backgroundColor.greenF(),
            self._backgroundColor.blueF(),
            1.0,
        )
        self._glIntialized = True

    def _onImageCleared(self) -> None:
        self._drawImage = None
        self._drawRect = QRect()

    def _sourceImage(self) -> Optional[QImage]:
        if self._liveImage is not None and not self._liveImage.isNull():
            return self._liveImage
        if self._image is not None and not self._image.isNull():
            return self._image.toImage()
        return None

    def _contentSize(self) -> tuple[int, int]:
        if self._contentW > 0 and self._contentH > 0:
            return self._contentW, self._contentH
        src = self._sourceImage()
        if src is None:
            return 0, 0
        return src.width(), src.height()

    def _fitRect(self, vw: int, vh: int, iw: int, ih: int) -> QRect:
        if vw <= 0 or vh <= 0 or iw <= 0 or ih <= 0:
            return QRect()
        mode = self._fitMode
        if mode is ImageFitMode.Fill:
            return QRect(0, 0, vw, vh)
        if mode is ImageFitMode.Scale:
            scale = min(vw / iw, vh / ih)
            tw = max(1, int(iw * scale))
            th = max(1, int(ih * scale))
            return QRect((vw - tw) // 2, (vh - th) // 2, tw, th)
        return QRect(0, 0, vw, vh)

    def _recompute(self) -> None:
        self._dirty = False
        self._drawImage = None
        self._drawRect = QRect()

        src = self._sourceImage()
        if src is None or src.isNull():
            return

        w = self.width()
        h = self.height()
        iw, ih = self._contentSize()
        if iw <= 0 or ih <= 0:
            iw, ih = src.width(), src.height()
        if w <= 0 or h <= 0 or iw <= 0 or ih <= 0:
            return

        self._drawRect = self._fitRect(w, h, iw, ih)
        mode = self._fitMode

        # Transitional: CPU scale into draw buffer. True GPU shader sampling
        # replaces this when external textures are bound.
        if mode is ImageFitMode.Fill:
            self._drawImage = src.scaled(
                w, h,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.FastTransformation,
            )
            return

        if mode is ImageFitMode.Scale:
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
