# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtCore import (
    QEasingCurve,
    QObject,
    QPoint,
    QPointF,
    QRect,
    Qt,
    QVariantAnimation,
)
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget

# ==================================================================================
from .__base import AnimationBase


# ==================================================================================
class _LightningOverlay(QWidget):
    """Full-window overlay that paints a bolt segment along a path."""

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent;")
        self._progress: float = 0.0
        self._start: QPointF = QPointF()
        self._end: QPointF = QPointF()
        self._boltColor: QColor = QColor("#ffca28")
        self._coreColor: QColor = QColor("#ffffff")

    def SetPath(self, start: QPointF, end: QPointF) -> None:
        self._start = start
        self._end = end

    def SetProgress(self, value: float) -> None:
        self._progress = max(0.0, min(1.0, float(value)))
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        if self._progress <= 0.0:
            return
        lPainter = QPainter(self)
        lPainter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        lT = self._progress
        lX = self._start.x() + (self._end.x() - self._start.x()) * lT
        lY = self._start.y() + (self._end.y() - self._start.y()) * lT
        lHead = QPointF(lX, lY)

        # Jagged bolt from start toward head
        lPath = QPainterPath(self._start)
        lDx = lHead.x() - self._start.x()
        lDy = lHead.y() - self._start.y()
        lSteps = 6
        for lI in range(1, lSteps + 1):
            lF = lI / lSteps
            lPx = self._start.x() + lDx * lF
            lPy = self._start.y() + lDy * lF
            # alternate lateral offset for zigzag
            lNx = -lDy
            lNy = lDx
            lLen = max(1.0, (lNx * lNx + lNy * lNy) ** 0.5)
            lOff = 8.0 * (1.0 if lI % 2 == 0 else -1.0) * (1.0 - lF * 0.3)
            lPx += (lNx / lLen) * lOff
            lPy += (lNy / lLen) * lOff
            lPath.lineTo(QPointF(lPx, lPy))
        lPath.lineTo(lHead)

        lGlow = QPen(QColor(self._boltColor.red(), self._boltColor.green(), self._boltColor.blue(), 90))
        lGlow.setWidth(8)
        lGlow.setCapStyle(Qt.PenCapStyle.RoundCap)
        lPainter.setPen(lGlow)
        lPainter.drawPath(lPath)

        lBolt = QPen(self._boltColor)
        lBolt.setWidth(3)
        lBolt.setCapStyle(Qt.PenCapStyle.RoundCap)
        lPainter.setPen(lBolt)
        lPainter.drawPath(lPath)

        lCore = QPen(self._coreColor)
        lCore.setWidth(1)
        lPainter.setPen(lCore)
        lPainter.drawPath(lPath)

        # Head flash
        lPainter.setBrush(self._coreColor)
        lPainter.setPen(Qt.PenStyle.NoPen)
        lPainter.drawEllipse(lHead, 4.0, 4.0)


# ==================================================================================
class LightningShootAnimation(AnimationBase):
    """Widget → lightning → shoot to destination → restore.

    Phase model (progress 0..1):
      0.00–0.20  compress / "transpose into bolt" (source fade)
      0.20–0.80  bolt travels source → destination
      0.80–1.00  expand / transpose back at destination

    Source and destination stay in the tree; visuals are overlay-only so layout
    is not disrupted. Callers hide/show real widgets around Start if desired.
    """

    def __init__(
        self,
        source: Optional[QWidget] = None,
        destination: Optional[QWidget] = None,
        durationMs: int = 480,
        easing: QEasingCurve.Type = QEasingCurve.Type.InOutCubic,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(target=source, durationMs=durationMs, easing=easing, parent=parent)
        self._source: Optional[QWidget] = source
        self._destination: Optional[QWidget] = destination
        self._overlay: Optional[_LightningOverlay] = None
        self._anim: Optional[QVariantAnimation] = None

    def SetEndpoints(self, source: QWidget, destination: QWidget) -> None:
        self._source = source
        self._destination = destination
        self._target = source

    def _hostWindow(self) -> Optional[QWidget]:
        if self._source is None:
            return None
        lWin = self._source.window()
        return lWin if isinstance(lWin, QWidget) else None

    def _centerInHost(self, widget: QWidget, host: QWidget) -> QPointF:
        lGlobal = widget.mapToGlobal(widget.rect().center())
        lLocal = host.mapFromGlobal(lGlobal)
        return QPointF(lLocal)

    def _onStart(self) -> None:
        if self._source is None or self._destination is None:
            self._emitFinished()
            return

        lHost = self._hostWindow()
        if lHost is None:
            self._emitFinished()
            return

        self._overlay = _LightningOverlay(lHost)
        self._overlay.setGeometry(lHost.rect())
        self._overlay.SetPath(
            self._centerInHost(self._source, lHost),
            self._centerInHost(self._destination, lHost),
        )
        self._overlay.show()
        self._overlay.raise_()

        # Optional: soft-hide source during travel
        self._source.setWindowOpacity(0.35)

        self._anim = QVariantAnimation(self)
        self._anim.setDuration(self._durationMs)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setEasingCurve(self._easing)
        self._anim.valueChanged.connect(self._onProgress)
        self._anim.finished.connect(self._onAnimFinished)
        self._anim.start()

    def _onProgress(self, value: object) -> None:
        lT = float(value)
        if self._overlay is not None:
            # Map full timeline so bolt motion occupies middle 60%
            if lT < 0.20:
                self._overlay.SetProgress(0.0)
            elif lT > 0.80:
                self._overlay.SetProgress(1.0)
            else:
                self._overlay.SetProgress((lT - 0.20) / 0.60)

        if self._source is not None:
            if lT < 0.20:
                self._source.setWindowOpacity(1.0 - (lT / 0.20) * 0.85)
            elif lT > 0.80:
                self._source.setWindowOpacity(0.15)
            else:
                self._source.setWindowOpacity(0.15)

        if self._destination is not None and lT > 0.80:
            lReveal = (lT - 0.80) / 0.20
            self._destination.setWindowOpacity(0.2 + 0.8 * lReveal)

    def _onStop(self) -> None:
        if self._anim is not None:
            self._anim.stop()
            self._anim = None
        self._cleanup()

    def _onAnimFinished(self) -> None:
        self._anim = None
        self._cleanup()
        self._emitFinished()

    def _cleanup(self) -> None:
        if self._source is not None:
            self._source.setWindowOpacity(1.0)
        if self._destination is not None:
            self._destination.setWindowOpacity(1.0)
        if self._overlay is not None:
            self._overlay.hide()
            self._overlay.deleteLater()
            self._overlay = None
