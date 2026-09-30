# ==================================================================================
# src/eNuts/UI/widgets/__evolvingNeuralOrb.py
# ==================================================================================
from __future__ import annotations

from math import cos, pi, sin
from typing import Optional

# ==================================================================================
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPen,
    QSurfaceFormat,
)
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QWidget

# ==================================================================================
try:
    from OpenGL.GL import (
        GL_BLEND,
        GL_COLOR_BUFFER_BIT,
        GL_DEPTH_BUFFER_BIT,
        GL_DEPTH_TEST,
        GL_LINE_SMOOTH,
        GL_LINES,
        GL_MODELVIEW,
        GL_ONE_MINUS_SRC_ALPHA,
        GL_POINTS,
        GL_POINT_SMOOTH,
        GL_PROJECTION,
        GL_SMOOTH,
        GL_SRC_ALPHA,
        glBegin,
        glBlendFunc,
        glClear,
        glClearColor,
        glColor4f,
        glEnable,
        glEnd,
        glLineWidth,
        glLoadIdentity,
        glMatrixMode,
        glPointSize,
        glRotatef,
        glShadeModel,
        glTranslatef,
        glVertex3f,
        glViewport,
    )
    from OpenGL.GLU import gluPerspective
except ImportError as ex:
    raise ImportError(
        "PyOpenGL is required for EvolvingNeuralOrb. "
        "pip install PyOpenGL PyOpenGL-accelerate"
    ) from ex


# ==================================================================================
class EvolvingNeuralOrb(QOpenGLWidget):
    """Revolving neural sphere with infinitely evolving mesh and reactive eNuts text.

    - Sphere rotates continuously (visible 3-D revolution).
    - Node mesh pulses / phase-shifts so the web looks alive and evolving.
    - "eNuts" wordmark uses a moving purple→cyan gradient driven by the same
      evolution phase as the mesh, so the text reacts to the network.
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        *,
        revolutionMs: int = 16,
        degreesPerTick: float = 0.45,
        evolutionSpeed: float = 0.035,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("EvolvingNeuralOrb")

        self._angleY: float = 0.0
        self._angleX: float = 22.0
        self._degreesPerTick: float = degreesPerTick
        self._evolutionPhase: float = 0.0
        self._evolutionSpeed: float = evolutionSpeed

        self._timer: QTimer = QTimer(self)
        self._timer.timeout.connect(self._onTick)
        self._timer.start(revolutionMs)

        lFmt = QSurfaceFormat()
        lFmt.setSamples(8)
        lFmt.setAlphaBufferSize(8)
        self.setFormat(lFmt)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    # ------------------------------------------------------------------ public API
    def SetRevolutionSpeed(self, degreesPerTick: float) -> None:
        self._degreesPerTick = degreesPerTick

    def SetEvolutionSpeed(self, speed: float) -> None:
        self._evolutionSpeed = speed

    def Pause(self) -> None:
        self._timer.stop()

    def Resume(self) -> None:
        if not self._timer.isActive():
            self._timer.start()

    @property
    def EvolutionPhase(self) -> float:
        """0..2π phase used by mesh and text gradient."""
        return self._evolutionPhase

    # ----------------------------------------------------------------- private slots
    def _onTick(self) -> None:
        self._angleY = (self._angleY + self._degreesPerTick) % 360.0
        self._evolutionPhase = (self._evolutionPhase + self._evolutionSpeed) % (2.0 * pi)
        self.update()

    # ---------------------------------------------------------------- OpenGL hooks
    def initializeGL(self) -> None:
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_POINT_SMOOTH)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glShadeModel(GL_SMOOTH)
        glClearColor(0.0, 0.0, 0.0, 0.0)

    def resizeGL(self, w: int, h: int) -> None:
        glViewport(0, 0, w, max(h, 1))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(42.0, w / max(h, 1), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self) -> None:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0.0, 0.08, -3.15)
        glRotatef(self._angleX, 1.0, 0.0, 0.0)
        glRotatef(self._angleY, 0.0, 1.0, 0.0)

        self._drawNeuralSphere(radius=1.0, latitudeBands=16, longitudeBands=28)

        # Overlay reactive eNuts wordmark (2-D, after GL)
        self._drawENutsLabel()

    # ---------------------------------------------------------------- mesh drawing
    def _meshColor(self, lonT: float, latT: float) -> tuple[float, float, float, float]:
        """Purple→cyan base shifted by evolution phase + latitude wave."""
        lPhase = self._evolutionPhase
        lWave = 0.5 + 0.5 * sin(lPhase + lonT * 2.0 * pi + latT * pi)
        lShift = 0.5 + 0.5 * sin(lPhase * 0.7 + lonT * pi)

        # purple (0.72, 0.15, 0.95) → cyan (0.05, 0.92, 0.98)
        lR = 0.72 * (1.0 - lShift) + 0.05 * lShift
        lG = 0.15 * (1.0 - lShift) + 0.92 * lShift
        lB = 0.95 * (1.0 - lShift) + 0.98 * lShift
        lA = 0.35 + 0.55 * lWave
        return (lR, lG, lB, lA)

    def _drawNeuralSphere(
        self, radius: float, latitudeBands: int, longitudeBands: int
    ) -> None:
        lPhase = self._evolutionPhase

        for lLat in range(latitudeBands):
            lTheta1 = lLat * pi / latitudeBands
            lTheta2 = (lLat + 1) * pi / latitudeBands
            lLatT = lLat / max(latitudeBands - 1, 1)

            for lLon in range(longitudeBands):
                lPhi1 = lLon * 2.0 * pi / longitudeBands
                lPhi2 = (lLon + 1) * 2.0 * pi / longitudeBands
                lLonT = lLon / longitudeBands

                lV1 = self._spherePoint(radius, lTheta1, lPhi1)
                lV2 = self._spherePoint(radius, lTheta1, lPhi2)
                lV3 = self._spherePoint(radius, lTheta2, lPhi1)
                lV4 = self._spherePoint(radius, lTheta2, lPhi2)

                lR, lG, lB, lA = self._meshColor(lLonT, lLatT)
                glColor4f(lR, lG, lB, lA)
                glLineWidth(1.15)

                glBegin(GL_LINES)
                glVertex3f(*lV1)
                glVertex3f(*lV2)
                glVertex3f(*lV1)
                glVertex3f(*lV3)
                glVertex3f(*lV2)
                glVertex3f(*lV4)
                glVertex3f(*lV3)
                glVertex3f(*lV4)
                glEnd()

                # Evolving node brightness / size
                lPulse = 0.55 + 0.45 * sin(
                    lPhase * 1.4 + lLonT * 4.0 * pi + lLatT * 2.0 * pi
                )
                lNodeR = min(lR + 0.25 * lPulse, 1.0)
                lNodeG = min(lG + 0.25 * lPulse, 1.0)
                lNodeB = min(lB + 0.20 * lPulse, 1.0)
                glColor4f(lNodeR, lNodeG, lNodeB, 0.55 + 0.45 * lPulse)
                glPointSize(2.2 + 3.2 * lPulse)
                glBegin(GL_POINTS)
                glVertex3f(*lV1)
                glEnd()

                # Occasional brighter "activation" nodes
                if (lLon + lLat) % 5 == 0:
                    lSpark = 0.4 + 0.6 * max(
                        0.0, sin(lPhase * 2.1 + lLonT * 6.0 * pi)
                    )
                    glColor4f(1.0, 1.0, 1.0, 0.35 * lSpark)
                    glPointSize(4.0 + 5.0 * lSpark)
                    glBegin(GL_POINTS)
                    glVertex3f(*lV1)
                    glEnd()

    @staticmethod
    def _spherePoint(radius: float, theta: float, phi: float) -> tuple[float, float, float]:
        lX = radius * sin(theta) * cos(phi)
        lY = radius * cos(theta)
        lZ = radius * sin(theta) * sin(phi)
        return (lX, lY, lZ)

    # ---------------------------------------------------------------- eNuts label
    def _evolutionGradientColors(self) -> tuple[QColor, QColor, QColor]:
        """Three stops for the text gradient, driven by mesh evolution phase."""
        lPhase = self._evolutionPhase
        lT = 0.5 + 0.5 * sin(lPhase)
        lT2 = 0.5 + 0.5 * sin(lPhase + 2.1)

        # Left: magenta/purple
        lC0 = QColor(
            int(180 + 60 * lT),
            int(40 + 80 * (1.0 - lT)),
            int(230 + 25 * lT),
        )
        # Mid: electric violet → teal
        lC1 = QColor(
            int(80 + 100 * (1.0 - lT2)),
            int(120 + 100 * lT2),
            int(240 - 40 * lT2),
        )
        # Right: cyan
        lC2 = QColor(
            int(20 + 40 * (1.0 - lT)),
            int(200 + 40 * lT),
            int(240 + 15 * (1.0 - lT)),
        )
        return (lC0, lC1, lC2)

    def _drawENutsLabel(self) -> None:
        lPainter = QPainter(self)
        lPainter.setRenderHint(QPainter.RenderHint.Antialiasing)
        lPainter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        lW = self.width()
        lH = self.height()
        if lW < 8 or lH < 8:
            lPainter.end()
            return

        lText = "eNuts"
        lPixel = max(18, int(min(lW, lH) * 0.14))
        lFont = QFont("Segoe UI", lPixel, QFont.Weight.Bold)
        lFont.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        lPainter.setFont(lFont)

        lMetrics = lPainter.fontMetrics()
        lTextW = lMetrics.horizontalAdvance(lText)
        lTextH = lMetrics.height()
        lX = (lW - lTextW) / 2.0
        # Lower third of the widget, matching logo placement
        lY = lH * 0.72 + lTextH * 0.35

        lC0, lC1, lC2 = self._evolutionGradientColors()
        lGrad = QLinearGradient(lX, 0, lX + lTextW, 0)
        lGrad.setColorAt(0.0, lC0)
        lGrad.setColorAt(0.5, lC1)
        lGrad.setColorAt(1.0, lC2)

        # Soft outer glow (reacts with same colors, lower alpha)
        for lGlow in (6, 3):
            lGlowPen = QPen(QColor(lC1.red(), lC1.green(), lC1.blue(), 35))
            lGlowPen.setWidth(lGlow)
            lPainter.setPen(lGlowPen)
            lPainter.drawText(int(lX), int(lY), lText)

        lPainter.setPen(QPen(lGrad, 1))
        lPainter.drawText(int(lX), int(lY), lText)

        lPainter.end()
