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
        GL_CULL_FACE,
        GL_DEPTH_BUFFER_BIT,
        GL_DEPTH_TEST,
        GL_FRONT_AND_BACK,
        GL_LIGHTING,
        GL_LINE_SMOOTH,
        GL_LINES,
        GL_MODELVIEW,
        GL_ONE,
        GL_ONE_MINUS_SRC_ALPHA,
        GL_POINTS,
        GL_POINT_SMOOTH,
        GL_PROJECTION,
        GL_QUAD_STRIP,
        GL_SMOOTH,
        GL_SRC_ALPHA,
        GL_TRIANGLE_STRIP,
        glBegin,
        glBlendFunc,
        glClear,
        glClearColor,
        glColor4f,
        glDepthMask,
        glDisable,
        glEnable,
        glEnd,
        glLineWidth,
        glLoadIdentity,
        glMatrixMode,
        glPointSize,
        glPolygonMode,
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
    """Logo-style revolving neural orb.

    Matches the eNuts logo look:
    - Solid dark spherical body with purple/cyan rim glow
    - Dense geodesic-style node mesh that evolves continuously
    - Metallic eNuts wordmark whose gradient reacts to mesh evolution
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        *,
        revolutionMs: int = 16,
        degreesPerTick: float = 0.35,
        evolutionSpeed: float = 0.028,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("EvolvingNeuralOrb")

        self._angleY: float = 0.0
        self._angleX: float = 16.0
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
        glDisable(GL_LIGHTING)
        glDisable(GL_CULL_FACE)
        glClearColor(0.0, 0.0, 0.0, 0.0)

    def resizeGL(self, w: int, h: int) -> None:
        glViewport(0, 0, w, max(h, 1))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(40.0, w / max(h, 1), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self) -> None:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0.0, 0.06, -3.05)
        glRotatef(self._angleX, 1.0, 0.0, 0.0)
        glRotatef(self._angleY, 0.0, 1.0, 0.0)

        # 1) Solid dark core (logo interior)
        self._drawSolidCore(radius=0.98, bands=48)

        # 2) Soft outer rim glow (purple-left / cyan-right)
        self._drawRimGlow(radius=1.02, bands=64)

        # 3) Dense evolving neural mesh on the surface
        self._drawNeuralMesh(radius=1.0, latitudeBands=20, longitudeBands=36)

        # 4) Reactive eNuts wordmark
        self._drawENutsLabel()

    # ---------------------------------------------------------------- geometry helpers
    @staticmethod
    def _spherePoint(radius: float, theta: float, phi: float) -> tuple[float, float, float]:
        lX = radius * sin(theta) * cos(phi)
        lY = radius * cos(theta)
        lZ = radius * sin(theta) * sin(phi)
        return (lX, lY, lZ)

    def _lonColor(self, lonT: float) -> tuple[float, float, float]:
        """Logo gradient: magenta/purple (left) → cyan (right), shifted by evolution."""
        lPhase = self._evolutionPhase
        lShift = (lonT + 0.15 * sin(lPhase)) % 1.0

        # purple/magenta → cyan
        lR = 0.85 * (1.0 - lShift) + 0.05 * lShift
        lG = 0.20 * (1.0 - lShift) + 0.95 * lShift
        lB = 0.98 * (1.0 - lShift) + 1.00 * lShift
        return (lR, lG, lB)

    # ---------------------------------------------------------------- solid core
    def _drawSolidCore(self, radius: float, bands: int) -> None:
        """Dark filled sphere — matches the logo's deep navy interior."""
        glDepthMask(True)
        for lLat in range(bands):
            lTheta1 = lLat * pi / bands
            lTheta2 = (lLat + 1) * pi / bands
            glBegin(GL_TRIANGLE_STRIP)
            for lLon in range(bands + 1):
                lPhi = lLon * 2.0 * pi / bands
                lLonT = lLon / bands
                lR, lG, lB = self._lonColor(lLonT)
                # Very dark, slight tint from the rim gradient
                glColor4f(lR * 0.08, lG * 0.10, lB * 0.18 + 0.05, 0.92)
                glVertex3f(*self._spherePoint(radius, lTheta1, lPhi))
                glVertex3f(*self._spherePoint(radius, lTheta2, lPhi))
            glEnd()

    # ---------------------------------------------------------------- rim glow
    def _drawRimGlow(self, radius: float, bands: int) -> None:
        """Soft luminous shell around the orb (logo edge glow)."""
        glDepthMask(False)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)  # additive
        lPhase = self._evolutionPhase
        lPulse = 0.75 + 0.25 * sin(lPhase)

        for lShell in range(3):
            lR = radius + 0.012 * lShell
            lAlpha = (0.12 - lShell * 0.03) * lPulse
            for lLat in range(bands // 2):
                lTheta1 = lLat * pi / (bands // 2)
                lTheta2 = (lLat + 1) * pi / (bands // 2)
                # Prefer equatorial rim brightness
                lEquator = sin((lTheta1 + lTheta2) * 0.5)
                glBegin(GL_TRIANGLE_STRIP)
                for lLon in range(bands + 1):
                    lPhi = lLon * 2.0 * pi / bands
                    lLonT = lLon / bands
                    lCr, lCg, lCb = self._lonColor(lLonT)
                    lA = lAlpha * (0.35 + 0.65 * lEquator)
                    glColor4f(lCr, lCg, lCb, lA)
                    glVertex3f(*self._spherePoint(lR, lTheta1, lPhi))
                    glVertex3f(*self._spherePoint(lR, lTheta2, lPhi))
                glEnd()

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDepthMask(True)

    # ---------------------------------------------------------------- neural mesh
    def _drawNeuralMesh(
        self, radius: float, latitudeBands: int, longitudeBands: int
    ) -> None:
        lPhase = self._evolutionPhase
        glDepthMask(False)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)

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

                lCr, lCg, lCb = self._lonColor(lLonT)
                lWave = 0.55 + 0.45 * sin(
                    lPhase + lLonT * 2.5 * pi + lLatT * 1.5 * pi
                )
                lA = 0.25 + 0.55 * lWave

                glColor4f(lCr, lCg, lCb, lA)
                glLineWidth(1.3)
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

                # Nodes
                lPulse = 0.5 + 0.5 * sin(
                    lPhase * 1.6 + lLonT * 5.0 * pi + lLatT * 3.0 * pi
                )
                glColor4f(
                    min(lCr + 0.35 * lPulse, 1.0),
                    min(lCg + 0.35 * lPulse, 1.0),
                    min(lCb + 0.25 * lPulse, 1.0),
                    0.45 + 0.55 * lPulse,
                )
                glPointSize(2.5 + 3.5 * lPulse)
                glBegin(GL_POINTS)
                glVertex3f(*lV1)
                glEnd()

                # Brighter activation sparks (logo hot-spots)
                if (lLon * 3 + lLat * 5) % 7 == 0:
                    lSpark = max(0.0, sin(lPhase * 2.3 + lLonT * 7.0 * pi))
                    if lSpark > 0.15:
                        glColor4f(1.0, 1.0, 1.0, 0.55 * lSpark)
                        glPointSize(4.5 + 6.0 * lSpark)
                        glBegin(GL_POINTS)
                        glVertex3f(*lV1)
                        glEnd()

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDepthMask(True)

    # ---------------------------------------------------------------- eNuts label
    def _evolutionGradientColors(self) -> tuple[QColor, QColor, QColor]:
        """Metallic purple→cyan stops, driven by mesh evolution."""
        lPhase = self._evolutionPhase
        lT = 0.5 + 0.5 * sin(lPhase)
        lT2 = 0.5 + 0.5 * sin(lPhase + 1.8)

        # Keep a metallic silver base, tinted by evolution
        lC0 = QColor(
            int(160 + 70 * lT),
            int(150 + 30 * (1.0 - lT)),
            int(200 + 40 * lT),
        )
        lC1 = QColor(
            int(120 + 80 * (1.0 - lT2)),
            int(160 + 70 * lT2),
            int(220 - 20 * lT2),
        )
        lC2 = QColor(
            int(80 + 40 * (1.0 - lT)),
            int(190 + 50 * lT),
            int(230 + 20 * (1.0 - lT)),
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
        lPixel = max(20, int(min(lW, lH) * 0.155))
        lFont = QFont("Segoe UI", lPixel, QFont.Weight.Bold)
        lFont.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.0)
        lFont.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        lPainter.setFont(lFont)

        lMetrics = lPainter.fontMetrics()
        lTextW = lMetrics.horizontalAdvance(lText)
        lTextH = lMetrics.height()
        lX = (lW - lTextW) / 2.0
        lY = lH * 0.70 + lTextH * 0.30

        lC0, lC1, lC2 = self._evolutionGradientColors()

        # Soft color glow behind text (reacts to mesh)
        for lGlow, lAlpha in ((10, 28), (5, 50)):
            lGlowPen = QPen(QColor(lC1.red(), lC1.green(), lC1.blue(), lAlpha))
            lGlowPen.setWidth(lGlow)
            lPainter.setPen(lGlowPen)
            lPainter.drawText(int(lX), int(lY), lText)

        # Metallic face gradient
        lGrad = QLinearGradient(lX, lY - lTextH, lX + lTextW, lY)
        lGrad.setColorAt(0.0, lC0)
        lGrad.setColorAt(0.45, QColor(230, 235, 245))
        lGrad.setColorAt(0.55, lC1)
        lGrad.setColorAt(1.0, lC2)

        lPainter.setPen(QPen(lGrad, 1))
        lPainter.drawText(int(lX), int(lY), lText)

        lPainter.end()
