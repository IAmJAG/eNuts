# ==================================================================================
from __future__ import annotations

# ==================================================================================
from math import cos, pi, sin
from typing import Callable, Optional

# ==================================================================================
from PySide6.QtCore import QEasingCurve, QObject, QPointF, QRectF, Qt, QVariantAnimation, Signal
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QRadialGradient
from PySide6.QtWidgets import QWidget

# ==================================================================================
from .__base import AnimationBase


# ==================================================================================
class _LightningOverlay(QWidget):
    """Paints: form lightning ball → tentacle to dest → rematerialize.

    Timeline (progress 0..1):
      0.00–0.22  source widget collapses into a lightning ball
      0.22–0.72  tentacle shoots from ball to destination edge
      0.72–1.00  ball reforms at dest and expands into panel silhouette
    """

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent;")

        self._progress: float = 0.0
        self._source: QPointF = QPointF()
        self._dest: QPointF = QPointF()
        self._sourceSize: QPointF = QPointF(48.0, 200.0)  # w, h of source silhouette
        self._destSize: QPointF = QPointF(48.0, 200.0)
        self._bolt = QColor("#ffca28")
        self._core = QColor("#ffffff")
        self._plasma = QColor("#e53935")

    def Configure(
        self,
        source: QPointF,
        dest: QPointF,
        sourceSize: QPointF,
        destSize: QPointF,
    ) -> None:
        self._source = source
        self._dest = dest
        self._sourceSize = sourceSize
        self._destSize = destSize

    def SetProgress(self, value: float) -> None:
        self._progress = max(0.0, min(1.0, float(value)))
        self.update()

    # ----------------------------------------------------------------------------------
    def paintEvent(self, event) -> None:  # noqa: N802
        lT = self._progress
        if lT <= 0.0:
            return

        lPainter = QPainter(self)
        lPainter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        if lT < 0.22:
            self._paintFormBall(lPainter, lT / 0.22)
        elif lT < 0.72:
            self._paintBall(lPainter, self._source, 1.0)
            self._paintTentacle(lPainter, (lT - 0.22) / 0.50)
        else:
            lReveal = (lT - 0.72) / 0.28
            # tentacle fully drawn, fading
            self._paintTentacle(lPainter, 1.0, alphaScale=max(0.0, 1.0 - lReveal))
            self._paintBall(lPainter, self._source, max(0.0, 1.0 - lReveal * 1.5))
            self._paintRematerialize(lPainter, lReveal)

    def _paintFormBall(self, painter: QPainter, t: float) -> None:
        """Source rect collapses into a ball."""
        lW = self._sourceSize.x() * (1.0 - t) + 22.0 * t
        lH = self._sourceSize.y() * (1.0 - t) + 22.0 * t
        lRect = QRectF(
            self._source.x() - lW * 0.5,
            self._source.y() - lH * 0.5,
            lW,
            lH,
        )
        lAlpha = int(40 + 140 * t)
        lFill = QColor(self._bolt.red(), self._bolt.green(), self._bolt.blue(), lAlpha)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(lFill)
        if t < 0.85:
            painter.drawRoundedRect(lRect, 4.0, 4.0)
        self._paintBall(painter, self._source, t)

    def _paintBall(self, painter: QPainter, center: QPointF, strength: float) -> None:
        if strength <= 0.05:
            return
        lR = 10.0 + 14.0 * strength
        lGrad = QRadialGradient(center, lR * 1.8)
        lGrad.setColorAt(
            0.0,
            QColor(self._core.red(), self._core.green(), self._core.blue(), int(230 * strength)),
        )
        lGrad.setColorAt(
            0.35,
            QColor(self._bolt.red(), self._bolt.green(), self._bolt.blue(), int(200 * strength)),
        )
        lGrad.setColorAt(
            0.7,
            QColor(self._plasma.red(), self._plasma.green(), self._plasma.blue(), int(90 * strength)),
        )
        lGrad.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(lGrad)
        painter.drawEllipse(center, lR * 1.8, lR * 1.8)

        # arc sparks around the ball
        lPen = QPen(QColor(self._bolt.red(), self._bolt.green(), self._bolt.blue(), int(180 * strength)))
        lPen.setWidthF(1.5)
        painter.setPen(lPen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for lI in range(5):
            lA0 = (lI / 5.0) * 2.0 * pi + strength * 2.0
            lA1 = lA0 + 0.7
            lPath = QPainterPath()
            lPath.moveTo(center.x() + cos(lA0) * lR * 0.6, center.y() + sin(lA0) * lR * 0.6)
            lPath.quadTo(
                center.x() + cos((lA0 + lA1) * 0.5) * lR * 1.4,
                center.y() + sin((lA0 + lA1) * 0.5) * lR * 1.4,
                center.x() + cos(lA1) * lR * 0.7,
                center.y() + sin(lA1) * lR * 0.7,
            )
            painter.drawPath(lPath)

    def _paintTentacle(
        self, painter: QPainter, t: float, alphaScale: float = 1.0
    ) -> None:
        if t <= 0.0 or alphaScale <= 0.0:
            return

        lHead = QPointF(
            self._source.x() + (self._dest.x() - self._source.x()) * t,
            self._source.y() + (self._dest.y() - self._source.y()) * t,
        )

        lPath = QPainterPath(self._source)
        lDx = lHead.x() - self._source.x()
        lDy = lHead.y() - self._source.y()
        lSteps = 10
        for lI in range(1, lSteps + 1):
            lF = lI / lSteps
            if lF > t:
                break
            lPx = self._source.x() + lDx * (lF / max(t, 0.001)) * t
            lPy = self._source.y() + lDy * (lF / max(t, 0.001)) * t
            # recompute along full t segment
            lPx = self._source.x() + (lHead.x() - self._source.x()) * lF
            lPy = self._source.y() + (lHead.y() - self._source.y()) * lF
            lNx = -(lHead.y() - self._source.y())
            lNy = lHead.x() - self._source.x()
            lLen = max(1.0, (lNx * lNx + lNy * lNy) ** 0.5)
            lOff = 16.0 * (1.0 if lI % 2 == 0 else -1.0) * (1.0 - lF * 0.3)
            lPx += (lNx / lLen) * lOff
            lPy += (lNy / lLen) * lOff
            lPath.lineTo(QPointF(lPx, lPy))
        lPath.lineTo(lHead)

        lA = int(110 * alphaScale)
        lGlow = QPen(QColor(self._bolt.red(), self._bolt.green(), self._bolt.blue(), lA))
        lGlow.setWidth(12)
        lGlow.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(lGlow)
        painter.drawPath(lPath)

        lBolt = QPen(
            QColor(self._bolt.red(), self._bolt.green(), self._bolt.blue(), int(220 * alphaScale))
        )
        lBolt.setWidth(3)
        lBolt.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(lBolt)
        painter.drawPath(lPath)

        lCore = QPen(QColor(255, 255, 255, int(200 * alphaScale)))
        lCore.setWidth(1)
        painter.setPen(lCore)
        painter.drawPath(lPath)

        # tentacle tip
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255, int(230 * alphaScale)))
        painter.drawEllipse(lHead, 5.0, 5.0)
        painter.setBrush(QColor(self._bolt.red(), self._bolt.green(), self._bolt.blue(), int(160 * alphaScale)))
        painter.drawEllipse(lHead, 9.0, 9.0)

    def _paintRematerialize(self, painter: QPainter, t: float) -> None:
        """Ball at dest expands into a panel silhouette."""
        self._paintBall(painter, self._dest, max(0.2, 1.0 - t * 0.5))

        lW = 22.0 * (1.0 - t) + self._destSize.x() * t
        lH = 22.0 * (1.0 - t) + self._destSize.y() * t
        lRect = QRectF(
            self._dest.x() - lW * 0.5,
            self._dest.y() - lH * 0.5,
            lW,
            lH,
        )
        lAlpha = int(30 + 100 * t)
        painter.setPen(
            QPen(
                QColor(self._bolt.red(), self._bolt.green(), self._bolt.blue(), int(160 * t)),
                2,
            )
        )
        painter.setBrush(
            QColor(self._bolt.red(), self._bolt.green(), self._bolt.blue(), lAlpha)
        )
        painter.drawRoundedRect(lRect, 3.0, 3.0)


# ==================================================================================
class LightningShootAnimation(AnimationBase):
    """Widget → lightning ball → tentacle to dest → rematerialize as widget.

    Signals:
      Midpoint  — tentacle has reached destination (safe time to reparent / flip dock)
    """

    Midpoint = Signal()

    def __init__(
        self,
        source: Optional[QWidget] = None,
        destination: Optional[QWidget] = None,
        durationMs: int = 720,
        easing: QEasingCurve.Type = QEasingCurve.Type.InOutCubic,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(target=source, durationMs=durationMs, easing=easing, parent=parent)
        self._source: Optional[QWidget] = source
        self._destination: Optional[QWidget] = destination
        self._pathStart: Optional[QPointF] = None
        self._pathEnd: Optional[QPointF] = None
        self._sourceSize: QPointF = QPointF(48.0, 240.0)
        self._destSize: QPointF = QPointF(48.0, 240.0)
        self._host: Optional[QWidget] = None
        self._hideSource: bool = True
        self._overlay: Optional[_LightningOverlay] = None
        self._anim: Optional[QVariantAnimation] = None
        self._midEmitted: bool = False
        self._onMidpoint: Optional[Callable[[], None]] = None

    def SetEndpoints(self, source: QWidget, destination: QWidget) -> None:
        self._source = source
        self._destination = destination
        self._target = source
        self._pathStart = None
        self._pathEnd = None

    def SetPathPoints(
        self,
        host: QWidget,
        start: QPointF,
        end: QPointF,
        sourceSize: Optional[QPointF] = None,
        destSize: Optional[QPointF] = None,
        hideSource: bool = True,
        onMidpoint: Optional[Callable[[], None]] = None,
    ) -> None:
        self._host = host
        self._pathStart = QPointF(start)
        self._pathEnd = QPointF(end)
        if sourceSize is not None:
            self._sourceSize = sourceSize
        if destSize is not None:
            self._destSize = destSize
        self._hideSource = hideSource
        self._onMidpoint = onMidpoint
        if self._source is None:
            self._source = host
            self._target = host

    def _hostWindow(self) -> Optional[QWidget]:
        if self._host is not None:
            return self._host
        if self._source is None:
            return None
        lWin = self._source.window()
        return lWin if isinstance(lWin, QWidget) else None

    def _centerInHost(self, widget: QWidget, host: QWidget) -> QPointF:
        lGlobal = widget.mapToGlobal(widget.rect().center())
        return QPointF(host.mapFromGlobal(lGlobal))

    def _onStart(self) -> None:
        lHost = self._hostWindow()
        if lHost is None:
            self._emitFinished()
            return

        if self._pathStart is not None and self._pathEnd is not None:
            lStart = self._pathStart
            lEnd = self._pathEnd
        elif self._source is not None and self._destination is not None:
            lStart = self._centerInHost(self._source, lHost)
            lEnd = self._centerInHost(self._destination, lHost)
            self._sourceSize = QPointF(float(self._source.width()), float(self._source.height()))
            self._destSize = QPointF(
                float(self._destination.width()), float(self._destination.height())
            )
        else:
            self._emitFinished()
            return

        self._midEmitted = False

        if self._hideSource and self._source is not None and self._source is not lHost:
            self._source.setVisible(False)

        self._overlay = _LightningOverlay(lHost)
        self._overlay.setGeometry(0, 0, lHost.width(), lHost.height())
        self._overlay.Configure(lStart, lEnd, self._sourceSize, self._destSize)
        self._overlay.show()
        self._overlay.raise_()

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
            self._overlay.SetProgress(lT)

        # Midpoint: tentacle arrives (start of rematerialize)
        if not self._midEmitted and lT >= 0.72:
            self._midEmitted = True
            self.Midpoint.emit()
            if self._onMidpoint is not None:
                self._onMidpoint()

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
        if self._hideSource and self._source is not None:
            self._source.setVisible(True)
        if self._overlay is not None:
            self._overlay.hide()
            self._overlay.deleteLater()
            self._overlay = None
