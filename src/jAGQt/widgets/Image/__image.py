# ==================================================================================
# src/jAGQt/widgets/Image/__image.py
# ==================================================================================
import os
from typing import Optional, Union

# ==================================================================================
from PySide6.QtCore import QPointF, QSize, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QImage,
    QPainter,
    QPaintEvent,
    QPixmap,
    QResizeEvent,
)
from PySide6.QtWidgets import QWidget
from torch import Tensor

# ==================================================================================
from ..components import ComponentBase


# ==================================================================================
class Image(QWidget, ComponentBase):
    """Software image display. Display only — no pan, zoom, or mouse interaction."""

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

        self._scaled: Optional[QPixmap] = None
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
    def zoom(self) -> float:
        return self._zoom

    @zoom.setter
    def zoom(self, value: float) -> None:
        lNew = max(1.0, min(value, 10_000.0))
        if abs(lNew - self._zoom) < 0.01:
            return
        self._zoom = lNew
        self._dirty = True
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
            self._scaled = None
            self._dirty = True
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
        self._dirty = True
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
        if self._image is not None and not self._image.isNull():
            self.resetView()
        super().resizeEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
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
