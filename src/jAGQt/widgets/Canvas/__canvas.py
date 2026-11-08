# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional, Union

# ==================================================================================
from PySide6.QtCore import Qt, Signal, SignalInstance
from PySide6.QtGui import (
    QColor,
    QFocusEvent,
    QImage,
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QPaintEvent,
    QPixmap,
    QResizeEvent,
)
from PySide6.QtWidgets import QSizePolicy, QWidget
from torch import Tensor

# ==================================================================================
from jAGFx.workflow import workflow

# ==================================================================================
from ..components import ComponentBase
from .__canvasBase import BACKGROUND_COLOR, CanvasBase
from .__fitMode import CanvasFitMode


# ==================================================================================
@workflow("InitializeUI", "InitializeBase")
class Canvas(QWidget, ComponentBase, CanvasBase):
    """Software canvas: static image + live present(Tensor|QImage) + input signals."""

    keyPressed: SignalInstance = Signal(object)
    keyReleased: SignalInstance = Signal(object)
    mousePressed: SignalInstance = Signal(object)
    mouseMoved: SignalInstance = Signal(object)
    mouseReleased: SignalInstance = Signal(object)

    def __init__(
        self,
        bg: Union[str, QColor] = BACKGROUND_COLOR,
        fitMode: CanvasFitMode = CanvasFitMode.Scale,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._backgroundColor = QColor(bg) if isinstance(bg, str) else bg
        self._fitMode: CanvasFitMode = fitMode
        self._scaled: Optional[QPixmap] = None
        self._liveImage: Optional[QImage] = None
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def _wInitializeUI(self) -> None:
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)

    # ------------------------------------------------------------------
    # iFrameView
    # ------------------------------------------------------------------
    def present(self, frame: Tensor | object) -> bool:
        image = self._frameToQImage(frame)
        if image is None or image.isNull():
            return False
        self._liveImage = image
        self._contentW = image.width()
        self._contentH = image.height()
        self._markDirty()
        return True

    def clear(self) -> None:
        self._liveImage = None
        self._scaled = None
        super().clear()

    # ------------------------------------------------------------------
    def _sourceImage(self) -> Optional[QImage]:
        if self._liveImage is not None and not self._liveImage.isNull():
            return self._liveImage
        return super()._sourceImage()

    def _onImageCleared(self) -> None:
        self._scaled = None
        self._drawRect = self._drawRect.__class__()

    def _frameToQImage(self, frame: object) -> Optional[QImage]:
        if isinstance(frame, QImage):
            return frame if not frame.isNull() else None
        if isinstance(frame, QPixmap):
            return frame.toImage() if not frame.isNull() else None
        if isinstance(frame, Tensor):
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
                warning(f"[Canvas] Tensor→QImage failed: {ex}")
                return None
        return None

    def _recompute(self) -> None:
        self._dirty = False
        self._scaled = None
        from PySide6.QtCore import QRect

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

        mode = self._fitMode
        pm = QPixmap.fromImage(src)

        if mode is CanvasFitMode.Fill:
            self._scaled = pm.scaled(
                w, h,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self._drawRect = QRect(0, 0, w, h)
            return

        if mode is CanvasFitMode.Scale:
            scale = min(w / iw, h / ih)
            tw = max(1, int(iw * scale))
            th = max(1, int(ih * scale))
            self._scaled = pm.scaled(
                tw, th,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self._drawRect = QRect((w - tw) // 2, (h - th) // 2, tw, th)
            return

        scale = max(w / iw, h / ih)
        tw = max(1, int(iw * scale))
        th = max(1, int(ih * scale))
        scaled = pm.scaled(
            tw, th,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._scaled = scaled.copy((tw - w) // 2, (th - h) // 2, w, h)
        self._drawRect = QRect(0, 0, w, h)

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

    # ------------------------------------------------------------------
    # input (from former CaptureImage)
    # ------------------------------------------------------------------
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
__all__ = ["Canvas"]
