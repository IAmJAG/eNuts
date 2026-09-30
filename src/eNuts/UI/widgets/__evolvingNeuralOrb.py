# ==================================================================================
# src/eNuts/UI/widgets/__evolvingNeuralOrb.py
# ==================================================================================
from __future__ import annotations

from array import array
from math import cos, pi, sin
from pathlib import Path
from typing import Optional

# ==================================================================================
from PySide6.QtCore import QThread, QTimer, Qt, Signal
from PySide6.QtGui import QImage, QSurfaceFormat
from PySide6.QtOpenGL import QOpenGLTexture
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QWidget

# ==================================================================================
try:
    from OpenGL.GL import (
        GL_ARRAY_BUFFER,
        GL_BLEND,
        GL_COLOR_ARRAY,
        GL_COLOR_BUFFER_BIT,
        GL_DEPTH_BUFFER_BIT,
        GL_DEPTH_TEST,
        GL_DYNAMIC_DRAW,
        GL_FLOAT,
        GL_LINES,
        GL_LINE_SMOOTH,
        GL_MODELVIEW,
        GL_ONE,
        GL_ONE_MINUS_SRC_ALPHA,
        GL_POINTS,
        GL_POINT_SMOOTH,
        GL_PROJECTION,
        GL_QUAD_STRIP,
        GL_SMOOTH,
        GL_SRC_ALPHA,
        GL_STATIC_DRAW,
        GL_TEXTURE_2D,
        GL_TRIANGLE_FAN,
        GL_VERTEX_ARRAY,
        glBegin,
        glBindBuffer,
        glBlendFunc,
        glBufferData,
        glClear,
        glClearColor,
        glColor4f,
        glColorPointer,
        glDeleteBuffers,
        glDisable,
        glDisableClientState,
        glDrawArrays,
        glEnable,
        glEnableClientState,
        glEnd,
        glGenBuffers,
        glLineWidth,
        glLoadIdentity,
        glMatrixMode,
        glPointSize,
        glRotatef,
        glShadeModel,
        glTexCoord2f,
        glTranslatef,
        glVertex3f,
        glVertexPointer,
        glViewport,
    )
    from OpenGL.GLU import gluPerspective
except ImportError as ex:
    raise ImportError(
        "PyOpenGL is required for EvolvingNeuralOrb. "
        "pip install PyOpenGL PyOpenGL-accelerate"
    ) from ex


# ==================================================================================
def _resolveLogoPath() -> Optional[Path]:
    """Locate assets/logo.png from common layout positions."""
    lHere = Path(__file__).resolve()
    # widgets -> UI -> eNuts -> src -> repo
    lRepo = lHere.parents[4] if len(lHere.parents) > 4 else lHere.parents[-1]
    lSrc = lHere.parents[3] if len(lHere.parents) > 3 else lHere.parents[-1]

    lCandidates = [
        lRepo / "assets" / "logo.png",
        lRepo / "assets" / "icons" / "logo.png",
        lSrc.parent / "assets" / "logo.png",
        Path.cwd() / "assets" / "logo.png",
        Path.cwd() / "assets" / "icons" / "logo.png",
        Path.cwd() / "logo.png",
    ]
    for lPath in lCandidates:
        try:
            if lPath.is_file():
                return lPath
        except OSError:
            continue
    return None


def _spherePoint(radius: float, theta: float, phi: float) -> tuple[float, float, float]:
    lX = radius * sin(theta) * cos(phi)
    lY = radius * cos(theta)
    lZ = radius * sin(theta) * sin(phi)
    return (lX, lY, lZ)


# ==================================================================================
class _MeshBakeWorker(QThread):
    """CPU-side bake of mesh positions + lonT attributes (no GL calls)."""

    Baked = Signal(object)

    def __init__(
        self,
        latitudeBands: int = 18,
        longitudeBands: int = 32,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._latitudeBands = latitudeBands
        self._longitudeBands = longitudeBands

    def run(self) -> None:
        lLatN = self._latitudeBands
        lLonN = self._longitudeBands
        lRadius = 1.005  # slightly outside textured sphere

        lLinePos = array("f")
        lLineLon = array("f")
        lNodePos = array("f")
        lNodeLon = array("f")
        lNodeLat = array("f")

        for lLat in range(lLatN):
            if self.isInterruptionRequested():
                return
            lTheta1 = lLat * pi / lLatN
            lTheta2 = (lLat + 1) * pi / lLatN
            lLatT = lLat / max(lLatN - 1, 1)

            for lLon in range(lLonN):
                lPhi1 = lLon * 2.0 * pi / lLonN
                lPhi2 = (lLon + 1) * 2.0 * pi / lLonN
                lLonT = lLon / lLonN

                lV1 = _spherePoint(lRadius, lTheta1, lPhi1)
                lV2 = _spherePoint(lRadius, lTheta1, lPhi2)
                lV3 = _spherePoint(lRadius, lTheta2, lPhi1)
                lV4 = _spherePoint(lRadius, lTheta2, lPhi2)

                for lA, lB in ((lV1, lV2), (lV1, lV3), (lV2, lV4), (lV3, lV4)):
                    lLinePos.extend(lA)
                    lLinePos.extend(lB)
                    lLineLon.append(lLonT)
                    lLineLon.append(lLonT)

                lNodePos.extend(lV1)
                lNodeLon.append(lLonT)
                lNodeLat.append(lLatT)

        self.Baked.emit(
            {
                "linePos": lLinePos,
                "lineLon": lLineLon,
                "nodePos": lNodePos,
                "nodeLon": lNodeLon,
                "nodeLat": lNodeLat,
                "lineCount": len(lLinePos) // 3,
                "nodeCount": len(lNodePos) // 3,
            }
        )


# ==================================================================================
class EvolvingNeuralOrb(QOpenGLWidget):
    """Logo texture sphere first; mesh VBO overlays when bake completes.

    Phase 1 — texture: spin logo.png (always visible if file found).
    Phase 2 — bake: background thread builds line/node positions.
    Phase 3 — mesh: VBO overlay on top of the textured sphere.
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        *,
        revolutionMs: int = 16,
        degreesPerTick: float = 0.35,
        evolutionSpeed: float = 0.028,
        logoPath: Optional[str | Path] = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("EvolvingNeuralOrb")

        self._angleY: float = 0.0
        self._angleX: float = 16.0
        self._degreesPerTick: float = degreesPerTick
        self._evolutionPhase: float = 0.0
        self._evolutionSpeed: float = evolutionSpeed

        self._logoPath: Optional[Path] = (
            Path(logoPath) if logoPath is not None else _resolveLogoPath()
        )

        self._texture: Optional[QOpenGLTexture] = None
        self._texReady: bool = False

        self._lineVbo: int = 0
        self._lineColorVbo: int = 0
        self._nodeVbo: int = 0
        self._nodeColorVbo: int = 0
        self._lineCount: int = 0
        self._nodeCount: int = 0
        self._lineLon: array = array("f")
        self._nodeLon: array = array("f")
        self._nodeLat: array = array("f")
        self._meshReady: bool = False
        self._pendingBake: Optional[dict] = None

        self._worker: Optional[_MeshBakeWorker] = None

        self._timer: QTimer = QTimer(self)
        self._timer.timeout.connect(self._onTick)
        self._timer.start(revolutionMs)

        lFmt = QSurfaceFormat()
        lFmt.setSamples(4)
        lFmt.setAlphaBufferSize(8)
        lFmt.setDepthBufferSize(24)
        self.setFormat(lFmt)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumSize(200, 200)

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

    @property
    def RenderMode(self) -> str:
        if self._meshReady:
            return "mesh"
        if self._texReady:
            return "texture"
        return "fallback"

    @property
    def LogoPath(self) -> Optional[Path]:
        return self._logoPath

    # ----------------------------------------------------------------- private slots
    def _onTick(self) -> None:
        self._angleY = (self._angleY + self._degreesPerTick) % 360.0
        self._evolutionPhase = (self._evolutionPhase + self._evolutionSpeed) % (2.0 * pi)
        self.update()

    def _onMeshBaked(self, payload: dict) -> None:
        self._pendingBake = payload
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

        self._loadLogoTexture()
        self._startMeshBake()

    def resizeGL(self, w: int, h: int) -> None:
        glViewport(0, 0, max(w, 1), max(h, 1))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(40.0, max(w, 1) / max(h, 1), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self) -> None:
        if self._pendingBake is not None:
            try:
                self._uploadMeshVbos(self._pendingBake)
                self._meshReady = True
            except Exception:
                self._meshReady = False
            self._pendingBake = None

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -3.2)
        glRotatef(self._angleX, 1.0, 0.0, 0.0)
        glRotatef(self._angleY, 0.0, 1.0, 0.0)

        # Always draw a visible base (texture or colored fallback)
        self._drawTexturedSphere()

        # Overlay evolving mesh when VBOs are ready
        if self._meshReady:
            self._drawMeshVbo()

    # ---------------------------------------------------------------- texture
    def _loadLogoTexture(self) -> None:
        self._texReady = False
        if self._texture is not None:
            self._texture.destroy()
            self._texture = None

        if self._logoPath is None or not self._logoPath.is_file():
            return

        lImage = QImage(str(self._logoPath))
        if lImage.isNull():
            return

        lImage = lImage.convertToFormat(QImage.Format.Format_RGBA8888)
        # OpenGL expects bottom-left origin
        lImage = lImage.flipped(Qt.Orientation.Vertical)

        try:
            lTex = QOpenGLTexture(QOpenGLTexture.Target.Target2D)
            lTex.setMinificationFilter(QOpenGLTexture.Filter.Linear)
            lTex.setMagnificationFilter(QOpenGLTexture.Filter.Linear)
            lTex.setWrapMode(QOpenGLTexture.WrapMode.ClampToEdge)
            lTex.setData(lImage)
            if not lTex.isCreated():
                return
            self._texture = lTex
            self._texReady = True
        except Exception:
            self._texture = None
            self._texReady = False

    def _drawTexturedSphere(self, radius: float = 1.0, bands: int = 40) -> None:
        if self._texReady and self._texture is not None:
            glEnable(GL_TEXTURE_2D)
            self._texture.bind()
            lPulse = 0.9 + 0.1 * sin(self._evolutionPhase)
            glColor4f(lPulse, lPulse, lPulse, 1.0)

            for lLat in range(bands):
                lTheta1 = lLat * pi / bands
                lTheta2 = (lLat + 1) * pi / bands
                lV1 = lLat / bands
                lV2 = (lLat + 1) / bands
                glBegin(GL_QUAD_STRIP)
                for lLon in range(bands + 1):
                    lPhi = lLon * 2.0 * pi / bands
                    lU = 1.0 - (lLon / bands)  # mirror U so logo faces camera better
                    lP1 = _spherePoint(radius, lTheta1, lPhi)
                    lP2 = _spherePoint(radius, lTheta2, lPhi)
                    glTexCoord2f(lU, lV1)
                    glVertex3f(*lP1)
                    glTexCoord2f(lU, lV2)
                    glVertex3f(*lP2)
                glEnd()

            self._texture.release()
            glDisable(GL_TEXTURE_2D)
            return

        # Fallback: visible purple→cyan sphere so we never stay pure black
        for lLat in range(24):
            lTheta1 = lLat * pi / 24
            lTheta2 = (lLat + 1) * pi / 24
            glBegin(GL_QUAD_STRIP)
            for lLon in range(25):
                lPhi = lLon * 2.0 * pi / 24
                lT = lLon / 24
                lR = 0.75 * (1.0 - lT) + 0.05 * lT
                lG = 0.20 * (1.0 - lT) + 0.90 * lT
                lB = 0.95
                glColor4f(lR, lG, lB, 0.95)
                glVertex3f(*_spherePoint(radius, lTheta1, lPhi))
                glVertex3f(*_spherePoint(radius, lTheta2, lPhi))
            glEnd()

    # ---------------------------------------------------------------- mesh bake / VBO
    def _startMeshBake(self) -> None:
        if self._worker is not None and self._worker.isRunning():
            return
        self._worker = _MeshBakeWorker(latitudeBands=16, longitudeBands=28, parent=self)
        self._worker.Baked.connect(self._onMeshBaked)
        self._worker.start()

    def _uploadMeshVbos(self, payload: dict) -> None:
        self._lineLon = payload["lineLon"]
        self._nodeLon = payload["nodeLon"]
        self._nodeLat = payload["nodeLat"]
        self._lineCount = int(payload["lineCount"])
        self._nodeCount = int(payload["nodeCount"])

        lLinePos = payload["linePos"]
        lNodePos = payload["nodePos"]

        for lAttr in ("_lineVbo", "_nodeVbo", "_lineColorVbo", "_nodeColorVbo"):
            lId = getattr(self, lAttr)
            if lId:
                glDeleteBuffers(1, [lId])
                setattr(self, lAttr, 0)

        self._lineVbo = int(glGenBuffers(1))
        glBindBuffer(GL_ARRAY_BUFFER, self._lineVbo)
        glBufferData(
            GL_ARRAY_BUFFER,
            memoryview(lLinePos).tobytes() if hasattr(lLinePos, "tobytes") else bytes(lLinePos),
            GL_STATIC_DRAW,
        )

        self._nodeVbo = int(glGenBuffers(1))
        glBindBuffer(GL_ARRAY_BUFFER, self._nodeVbo)
        glBufferData(
            GL_ARRAY_BUFFER,
            memoryview(lNodePos).tobytes() if hasattr(lNodePos, "tobytes") else bytes(lNodePos),
            GL_STATIC_DRAW,
        )

        self._lineColorVbo = int(glGenBuffers(1))
        self._nodeColorVbo = int(glGenBuffers(1))
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def _fillColors(self, lonArr: array, latArr: Optional[array], count: int) -> bytes:
        lPhase = self._evolutionPhase
        lColors = array("f")
        for lI in range(count):
            lLonT = lonArr[lI] if lI < len(lonArr) else 0.0
            lLatT = latArr[lI] if latArr is not None and lI < len(latArr) else 0.5
            lShift = (lLonT + 0.15 * sin(lPhase)) % 1.0
            lR = 0.85 * (1.0 - lShift) + 0.05 * lShift
            lG = 0.20 * (1.0 - lShift) + 0.95 * lShift
            lB = 0.98 * (1.0 - lShift) + 1.00 * lShift
            lWave = 0.55 + 0.45 * sin(lPhase + lLonT * 2.5 * pi + lLatT * 1.5 * pi)
            lA = 0.45 + 0.50 * lWave
            lColors.extend((lR, lG, lB, lA))
        return lColors.tobytes()

    def _drawMeshVbo(self) -> None:
        if self._lineCount <= 0 or self._lineVbo == 0:
            return

        lLineColors = self._fillColors(self._lineLon, None, self._lineCount)
        glBindBuffer(GL_ARRAY_BUFFER, self._lineColorVbo)
        glBufferData(GL_ARRAY_BUFFER, lLineColors, GL_DYNAMIC_DRAW)

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)

        glBindBuffer(GL_ARRAY_BUFFER, self._lineVbo)
        glVertexPointer(3, GL_FLOAT, 0, None)
        glBindBuffer(GL_ARRAY_BUFFER, self._lineColorVbo)
        glColorPointer(4, GL_FLOAT, 0, None)

        glLineWidth(1.4)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glDrawArrays(GL_LINES, 0, self._lineCount)

        if self._nodeCount > 0 and self._nodeVbo:
            lNodeColors = self._fillColors(self._nodeLon, self._nodeLat, self._nodeCount)
            glBindBuffer(GL_ARRAY_BUFFER, self._nodeColorVbo)
            glBufferData(GL_ARRAY_BUFFER, lNodeColors, GL_DYNAMIC_DRAW)

            glBindBuffer(GL_ARRAY_BUFFER, self._nodeVbo)
            glVertexPointer(3, GL_FLOAT, 0, None)
            glBindBuffer(GL_ARRAY_BUFFER, self._nodeColorVbo)
            glColorPointer(4, GL_FLOAT, 0, None)

            glPointSize(3.8)
            glDrawArrays(GL_POINTS, 0, self._nodeCount)

        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def closeEvent(self, event) -> None:
        if self._worker is not None and self._worker.isRunning():
            self._worker.requestInterruption()
            self._worker.wait(400)

        self.makeCurrent()
        if self._texture is not None:
            self._texture.destroy()
            self._texture = None
        for lAttr in ("_lineVbo", "_nodeVbo", "_lineColorVbo", "_nodeColorVbo"):
            lId = getattr(self, lAttr, 0)
            if lId:
                glDeleteBuffers(1, [lId])
                setattr(self, lAttr, 0)
        self.doneCurrent()
        super().closeEvent(event)
