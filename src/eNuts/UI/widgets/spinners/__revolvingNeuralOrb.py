# ==================================================================================
# src/eNuts/UI/widgets/__revolvingNeuralOrb.py
# ==================================================================================
from math import cos, pi, sin
from typing import Optional

# ==================================================================================
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QSurfaceFormat
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QWidget

# ==================================================================================
try:
    from OpenGL.GL import (
        GL_COLOR_BUFFER_BIT,
        GL_DEPTH_BUFFER_BIT,
        GL_DEPTH_TEST,
        GL_LINES,
        GL_MODELVIEW,
        GL_PROJECTION,
        GL_SMOOTH,
        glBegin,
        glClear,
        glClearColor,
        glColor3f,
        glEnable,
        glEnd,
        glLoadIdentity,
        glMatrixMode,
        glRotatef,
        glShadeModel,
        glTranslatef,
        glVertex3f,
        glViewport,
    )
    from OpenGL.GLU import gluPerspective

except ImportError as ex:
    raise ImportError(
        "PyOpenGL is required for RevolvingNeuralOrb. "
        "pip install PyOpenGL PyOpenGL-accelerate"
    ) from ex


# ==================================================================================
class RevolvingNeuralOrb(QOpenGLWidget):
    """Continuously revolving neural-web sphere (Option-5 style)."""

    def __init__(
        self, parent: Optional[QWidget] = None, *,
        revolutionMs: int = 16, degreesPerTick: float = 0.6,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("RevolvingNeuralOrb")

        self._angleY: float = 0.0
        self._angleX: float = 18.0
        self._degreesPerTick: float = degreesPerTick
        self._timer: QTimer = QTimer(self)
        self._timer.timeout.connect(self._onTick)
        self._timer.start(revolutionMs)

        lFmt = QSurfaceFormat()
        lFmt.setSamples(8)
        lFmt.setAlphaBufferSize(8)
        self.setFormat(lFmt)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

# ================================================================================== public API
    def SetRevolutionSpeed(self, degreesPerTick: float) -> None:
        """Positive = clockwise, negative = counter-clockwise."""
        self._degreesPerTick = degreesPerTick

    def Pause(self) -> None:
        self._timer.stop()

    def Resume(self) -> None:
        if not self._timer.isActive():
            self._timer.start()

# ================================================================================== private slots
    def _onTick(self) -> None:
        self._angleY = (self._angleY + self._degreesPerTick) % 360.0
        self.update()

# ================================================================================== OpenGL hooks
    def initializeGL(self) -> None:
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)
        glClearColor(0.0, 0.0, 0.0, 0.0)

    def resizeGL(self, w: int, h: int) -> None:
        glViewport(0, 0, w, max(h, 1))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, w / max(h, 1), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self) -> None:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -3.2)
        glRotatef(self._angleX, 1.0, 0.0, 0.0)
        glRotatef(self._angleY, 0.0, 1.0, 0.0)
        self._drawNeuralSphere(radius=1.0, latitudeBands=18, longitudeBands=24)

# ================================================================================== drawing helpers
    def _drawNeuralSphere(self, radius: float, latitudeBands: int, longitudeBands: int) -> None:
        for lLat in range(latitudeBands):
            lTheta1 = lLat * pi / latitudeBands
            lTheta2 = (lLat + 1) * pi / latitudeBands

            for lLon in range(longitudeBands):
                lPhi1 = lLon * 2.0 * pi / longitudeBands
                lPhi2 = (lLon + 1) * 2.0 * pi / longitudeBands

                lV1 = self._spherePoint(radius, lTheta1, lPhi1)
                lV2 = self._spherePoint(radius, lTheta1, lPhi2)
                lV3 = self._spherePoint(radius, lTheta2, lPhi1)
                lV4 = self._spherePoint(radius, lTheta2, lPhi2)

                lT = lLon / longitudeBands
                lR = 0.7 * (1.0 - lT) + 0.0 * lT
                lG = 0.2 * (1.0 - lT) + 0.9 * lT
                lB = 0.9 * (1.0 - lT) + 0.95 * lT
                glColor3f(lR, lG, lB)

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

                glColor3f(min(lR + 0.3, 1.0), min(lG + 0.3, 1.0), min(lB + 0.3, 1.0))
                self._drawNode(lV1, 0.025)
                self._drawNode(lV2, 0.025)

    @staticmethod
    def _spherePoint(radius: float, theta: float, phi: float) -> tuple[float, float, float]:
        lX = radius * sin(theta) * cos(phi)
        lY = radius * cos(theta)
        lZ = radius * sin(theta) * sin(phi)
        return (lX, lY, lZ)

    @staticmethod
    def _drawNode(pos: tuple[float, float, float], size: float) -> None:
        lX, lY, lZ = pos
        glBegin(GL_LINES)
        glVertex3f(lX - size, lY, lZ)
        glVertex3f(lX + size, lY, lZ)
        glVertex3f(lX, lY - size, lZ)
        glVertex3f(lX, lY + size, lZ)
        glEnd()
