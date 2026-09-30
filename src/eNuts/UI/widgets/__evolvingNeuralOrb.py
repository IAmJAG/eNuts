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
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QWidget

# ==================================================================================
try:
    from OpenGL.GL import (
        GL_ARRAY_BUFFER,
        GL_BLEND,
        GL_CLAMP_TO_EDGE,
        GL_COLOR_ARRAY,
        GL_COLOR_BUFFER_BIT,
        GL_DEPTH_BUFFER_BIT,
        GL_DEPTH_TEST,
        GL_DYNAMIC_DRAW,
        GL_FLOAT,
        GL_LINEAR,
        GL_LINES,
        GL_LINE_SMOOTH,
        GL_MODELVIEW,
        GL_ONE,
        GL_ONE_MINUS_SRC_ALPHA,
        GL_POINTS,
        GL_POINT_SMOOTH,
        GL_PROJECTION,
        GL_QUADS,
        GL_RGBA,
        GL_SMOOTH,
        GL_SRC_ALPHA,
        GL_STATIC_DRAW,
        GL_TEXTURE_2D,
        GL_TEXTURE_COORD_ARRAY,
        GL_TEXTURE_MAG_FILTER,
        GL_TEXTURE_MIN_FILTER,
        GL_TEXTURE_WRAP_S,
        GL_TEXTURE_WRAP_T,
        GL_TRIANGLES,
        GL_UNSIGNED_BYTE,
        GL_VERTEX_ARRAY,
        glBindBuffer,
        glBindTexture,
        glBlendFunc,
        glBufferData,
        glClear,
        glClearColor,
        glColorPointer,
        glDeleteBuffers,
        glDeleteTextures,
        glDisable,
        glDisableClientState,
        glDrawArrays,
        glEnable,
        glEnableClientState,
        glGenBuffers,
        glGenTextures,
        glLineWidth,
        glLoadIdentity,
        glMatrixMode,
        glPointSize,
        glRotatef,
        glShadeModel,
        glTexCoordPointer,
        glTexImage2D,
        glTexParameteri,
        glTranslatef,
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
    lHere = Path(__file__).resolve()
    lCandidates = [
        lHere.parents[3] / "assets" / "logo.png",          # repo/assets (from src/...)
        lHere.parents[3] / "assets" / "icons" / "logo.png",
        lHere.parents[4] / "assets" / "logo.png",
        Path("assets") / "logo.png",
        Path("assets") / "icons" / "logo.png",
    ]
    for lPath in lCandidates:
        if lPath.is_file():
            return lPath
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
        lRadius = 1.0

        lLinePos = array("f")
        lLineLon = array("f")
        lNodePos = array("f")
        lNodeLon = array("f")
        lNodeLat = array("f")

        for lLat in range(lLatN):
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

                # 4 edges as line segments (8 vertices)
                for lA, lB in ((lV1, lV2), (lV1, lV3), (lV2, lV4), (lV3, lV4)):
                    lLinePos.extend(lA)
                    lLinePos.extend(lB)
                    lLineLon.append(lLonT)
                    lLineLon.append(lLonT)

                lNodePos.extend(lV1)
                lNodeLon.append(lLonT)
                lNodeLat.append(lLatT)

        # Textured-sphere fallback geometry is not baked here.
        lPayload = {
            "linePos": lLinePos,
            "lineLon": lLineLon,
            "nodePos": lNodePos,
            "nodeLon": lNodeLon,
            "nodeLat": lNodeLat,
            "lineCount": len(lLinePos) // 3,
            "nodeCount": len(lNodePos) // 3,
        }
        self.Baked.emit(lPayload)


# ==================================================================================
class EvolvingNeuralOrb(QOpenGLWidget):
    """Logo texture sphere first; when mesh VBO is ready, switch to cached mesh.

    Phase 1 — texture: spin assets/logo.png on a UV sphere (smooth, logo-accurate).
    Phase 2 — bake: background thread builds line/node positions.
    Phase 3 — mesh: upload VBOs and take over rendering with evolving colors.
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

        self._renderMode: str = "texture"  # "texture" | "mesh"
        self._logoPath: Optional[Path] = (
            Path(logoPath) if logoPath is not None else _resolveLogoPath()
        )

        self._texId: int = 0
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

    @property
    def RenderMode(self) -> str:
        return self._renderMode

    # ----------------------------------------------------------------- private slots
    def _onTick(self) -> None:
        self._angleY = (self._angleY + self._degreesPerTick) % 360.0
        self._evolutionPhase = (self._evolutionPhase + self._evolutionSpeed) % (2.0 * pi)
        self.update()

    def _onMeshBaked(self, payload: dict) -> None:
        """Receive CPU bake; upload on the GL thread at next paint."""
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
        glViewport(0, 0, w, max(h, 1))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(40.0, w / max(h, 1), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self) -> None:
        if self._pendingBake is not None:
            self._uploadMeshVbos(self._pendingBake)
            self._pendingBake = None
            self._meshReady = True
            self._renderMode = "mesh"

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -3.1)
        glRotatef(self._angleX, 1.0, 0.0, 0.0)
        glRotatef(self._angleY, 0.0, 1.0, 0.0)

        if self._renderMode == "mesh" and self._meshReady:
            self._drawMeshVbo()
        else:
            self._drawTexturedSphere()

    def closeEvent(self, event) -> None:
        self._shutdownGl()
        super().closeEvent(event)

    # ---------------------------------------------------------------- texture phase
    def _loadLogoTexture(self) -> None:
        if self._logoPath is None or not self._logoPath.is_file():
            self._texReady = False
            return

        lImage = QImage(str(self._logoPath))
        if lImage.isNull():
            self._texReady = False
            return

        lImage = lImage.convertToFormat(QImage.Format.Format_RGBA8888)
        lImage = lImage.mirrored(False, True)  # OpenGL origin

        self._texId = int(glGenTextures(1))
        glBindTexture(GL_TEXTURE_2D, self._texId)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        lPtr = lImage.bits()
        lPtr.setsize(lImage.sizeInBytes())
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGBA,
            lImage.width(),
            lImage.height(),
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            bytes(lPtr),
        )
        glBindTexture(GL_TEXTURE_2D, 0)
        self._texReady = True

    def _drawTexturedSphere(self, radius: float = 1.0, bands: int = 48) -> None:
        """Smooth logo sphere while mesh is baking."""
        if not self._texReady:
            # Flat fallback disc tint
            glColor4f = __import__("OpenGL.GL", fromlist=["glColor4f"]).glColor4f
            glBegin = __import__("OpenGL.GL", fromlist=["glBegin"]).glBegin
            glEnd = __import__("OpenGL.GL", fromlist=["glEnd"]).glEnd
            glVertex3f = __import__("OpenGL.GL", fromlist=["glVertex3f"]).glVertex3f
            from OpenGL.GL import GL_TRIANGLE_FAN

            glColor4f(0.3, 0.1, 0.5, 0.9)
            glBegin(GL_TRIANGLE_FAN)
            glVertex3f(0.0, 0.0, 0.0)
            for lI in range(33):
                lA = lI * 2.0 * pi / 32
                glVertex3f(cos(lA) * radius, sin(lA) * radius, 0.0)
            glEnd()
            return

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self._texId)

        # Mild evolution tint over the logo
        lPulse = 0.85 + 0.15 * sin(self._evolutionPhase)
        from OpenGL.GL import glColor4f, glBegin, glEnd, glTexCoord2f, glVertex3f, GL_QUAD_STRIP

        glColor4f(lPulse, lPulse, lPulse, 1.0)

        for lLat in range(bands):
            lTheta1 = lLat * pi / bands
            lTheta2 = (lLat + 1) * pi / bands
            lV1 = lLat / bands
            lV2 = (lLat + 1) / bands
            glBegin(GL_QUAD_STRIP)
            for lLon in range(bands + 1):
                lPhi = lLon * 2.0 * pi / bands
                lU = lLon / bands
                lP1 = _spherePoint(radius, lTheta1, lPhi)
                lP2 = _spherePoint(radius, lTheta2, lPhi)
                glTexCoord2f(lU, lV1)
                glVertex3f(*lP1)
                glTexCoord2f(lU, lV2)
                glVertex3f(*lP2)
            glEnd()

        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_TEXTURE_2D)

    # ---------------------------------------------------------------- mesh bake / VBO
    def _startMeshBake(self) -> None:
        if self._worker is not None and self._worker.isRunning():
            return
        self._worker = _MeshBakeWorker(latitudeBands=18, longitudeBands=32, parent=self)
        self._worker.Baked.connect(self._onMeshBaked)
        self._worker.start()

    def _uploadMeshVbos(self, payload: dict) -> None:
        self._lineLon = payload["lineLon"]
        self._nodeLon = payload["nodeLon"]
        self._nodeLat = payload["nodeLat"]
        self._lineCount = payload["lineCount"]
        self._nodeCount = payload["nodeCount"]

        lLinePos = payload["linePos"]
        lNodePos = payload["nodePos"]

        if self._lineVbo:
            glDeleteBuffers(1, [self._lineVbo])
        if self._nodeVbo:
            glDeleteBuffers(1, [self._nodeVbo])
        if self._lineColorVbo:
            glDeleteBuffers(1, [self._lineColorVbo])
        if self._nodeColorVbo:
            glDeleteBuffers(1, [self._nodeColorVbo])

        self._lineVbo = int(glGenBuffers(1))
        glBindBuffer(GL_ARRAY_BUFFER, self._lineVbo)
        glBufferData(GL_ARRAY_BUFFER, lLinePos.tobytes(), GL_STATIC_DRAW)

        self._nodeVbo = int(glGenBuffers(1))
        glBindBuffer(GL_ARRAY_BUFFER, self._nodeVbo)
        glBufferData(GL_ARRAY_BUFFER, lNodePos.tobytes(), GL_STATIC_DRAW)

        # Color buffers — dynamic, filled each frame from evolution phase
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
            lA = 0.30 + 0.55 * lWave
            lColors.extend((lR, lG, lB, lA))
        return lColors.tobytes()

    def _drawMeshVbo(self) -> None:
        # --- lines ---
        lLineColors = self._fillColors(self._lineLon, None, self._lineCount)
        glBindBuffer(GL_ARRAY_BUFFER, self._lineColorVbo)
        glBufferData(GL_ARRAY_BUFFER, lLineColors, GL_DYNAMIC_DRAW)

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)

        glBindBuffer(GL_ARRAY_BUFFER, self._lineVbo)
        glVertexPointer(3, GL_FLOAT, 0, None)
        glBindBuffer(GL_ARRAY_BUFFER, self._lineColorVbo)
        glColorPointer(4, GL_FLOAT, 0, None)

        glLineWidth(1.25)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glDrawArrays(GL_LINES, 0, self._lineCount)

        # --- nodes ---
        lNodeColors = self._fillColors(self._nodeLon, self._nodeLat, self._nodeCount)
        glBindBuffer(GL_ARRAY_BUFFER, self._nodeColorVbo)
        glBufferData(GL_ARRAY_BUFFER, lNodeColors, GL_DYNAMIC_DRAW)

        glBindBuffer(GL_ARRAY_BUFFER, self._nodeVbo)
        glVertexPointer(3, GL_FLOAT, 0, None)
        glBindBuffer(GL_ARRAY_BUFFER, self._nodeColorVbo)
        glColorPointer(4, GL_FLOAT, 0, None)

        glPointSize(3.5)
        glDrawArrays(GL_POINTS, 0, self._nodeCount)

        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def _shutdownGl(self) -> None:
        if self._worker is not None and self._worker.isRunning():
            self._worker.requestInterruption()
            self._worker.wait(500)

        self.makeCurrent()
        if self._texId:
            glDeleteTextures([self._texId])
            self._texId = 0
        for lAttr in ("_lineVbo", "_nodeVbo", "_lineColorVbo", "_nodeColorVbo"):
            lId = getattr(self, lAttr, 0)
            if lId:
                glDeleteBuffers(1, [lId])
                setattr(self, lAttr, 0)
        self.doneCurrent()
