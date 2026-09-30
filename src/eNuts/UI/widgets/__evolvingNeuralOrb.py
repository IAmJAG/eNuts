# ==================================================================================
# src/eNuts/UI/widgets/__evolvingNeuralOrb.py
# ==================================================================================
from __future__ import annotations

from array import array
from math import cos, pi, sin
from typing import Optional

# ==================================================================================
from PySide6.QtCore import QThread, QTimer, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPalette,
    QPen,
    QSurfaceFormat,
)
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
        GL_TRIANGLES,
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
        glDepthMask,
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
def _spherePoint(radius: float, theta: float, phi: float) -> tuple[float, float, float]:
    lX = radius * sin(theta) * cos(phi)
    lY = radius * cos(theta)
    lZ = radius * sin(theta) * sin(phi)
    return (lX, lY, lZ)


# ==================================================================================
class _MeshBakeWorker(QThread):
    """Bake core + line + node geometry on CPU (no GL)."""

    Baked = Signal(object)

    def __init__(
        self,
        coreBands: int = 36,
        meshLat: int = 18,
        meshLon: int = 32,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._coreBands = coreBands
        self._meshLat = meshLat
        self._meshLon = meshLon

    def run(self) -> None:
        if self.isInterruptionRequested():
            return

        lCorePos = array("f")
        lCoreLon = array("f")
        lBands = self._coreBands
        lCoreR = 0.97
        for lLat in range(lBands):
            if self.isInterruptionRequested():
                return
            lTheta1 = lLat * pi / lBands
            lTheta2 = (lLat + 1) * pi / lBands
            for lLon in range(lBands):
                lPhi1 = lLon * 2.0 * pi / lBands
                lPhi2 = (lLon + 1) * 2.0 * pi / lBands
                lLonT = (lLon + 0.5) / lBands
                lA = _spherePoint(lCoreR, lTheta1, lPhi1)
                lB = _spherePoint(lCoreR, lTheta1, lPhi2)
                lC = _spherePoint(lCoreR, lTheta2, lPhi1)
                lD = _spherePoint(lCoreR, lTheta2, lPhi2)
                for lP in (lA, lB, lC, lB, lD, lC):
                    lCorePos.extend(lP)
                    lCoreLon.append(lLonT)

        lLinePos = array("f")
        lLineLon = array("f")
        lNodePos = array("f")
        lNodeLon = array("f")
        lNodeLat = array("f")
        lLatN = self._meshLat
        lLonN = self._meshLon
        lMeshR = 1.0

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
                lV1 = _spherePoint(lMeshR, lTheta1, lPhi1)
                lV2 = _spherePoint(lMeshR, lTheta1, lPhi2)
                lV3 = _spherePoint(lMeshR, lTheta2, lPhi1)
                lV4 = _spherePoint(lMeshR, lTheta2, lPhi2)
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
                "corePos": lCorePos,
                "coreLon": lCoreLon,
                "coreCount": len(lCorePos) // 3,
                "linePos": lLinePos,
                "lineLon": lLineLon,
                "lineCount": len(lLinePos) // 3,
                "nodePos": lNodePos,
                "nodeLon": lNodeLon,
                "nodeLat": lNodeLat,
                "nodeCount": len(lNodePos) // 3,
            }
        )


# ==================================================================================
class EvolvingNeuralOrb(QOpenGLWidget):
    """True 3D reconstruction of the eNuts logo with a transparent widget background."""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        *,
        revolutionMs: int = 16,
        degreesPerTick: float = 0.4,
        evolutionSpeed: float = 0.03,
    ) -> None:
        # Alpha-capable surface before the native window is created
        lFmt = QSurfaceFormat()
        lFmt.setSamples(4)
        lFmt.setAlphaBufferSize(8)
        lFmt.setDepthBufferSize(24)
        lFmt.setStencilBufferSize(0)
        lFmt.setSwapBehavior(QSurfaceFormat.SwapBehavior.DoubleBuffer)
        lFmt.setRenderableType(QSurfaceFormat.RenderableType.OpenGL)

        super().__init__(parent)
        self.setObjectName("EvolvingNeuralOrb")
        self.setFormat(lFmt)

        # Transparent widget chrome (no opaque system / style fill)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)
        self.setAutoFillBackground(False)
        self.setStyleSheet("background: transparent; border: none;")

        lPalette = self.palette()
        lPalette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0, 0))
        lPalette.setColor(QPalette.ColorRole.Base, QColor(0, 0, 0, 0))
        self.setPalette(lPalette)

        self._angleY: float = 0.0
        self._angleX: float = 18.0
        self._degreesPerTick: float = degreesPerTick
        self._evolutionPhase: float = 0.0
        self._evolutionSpeed: float = evolutionSpeed

        self._meshReady: bool = False
        self._pendingBake: Optional[dict] = None
        self._worker: Optional[_MeshBakeWorker] = None

        self._coreVbo = self._coreColorVbo = 0
        self._lineVbo = self._lineColorVbo = 0
        self._nodeVbo = self._nodeColorVbo = 0
        self._coreCount = self._lineCount = self._nodeCount = 0
        self._coreLon: array = array("f")
        self._lineLon: array = array("f")
        self._nodeLon: array = array("f")
        self._nodeLat: array = array("f")

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._onTick)
        self._timer.start(revolutionMs)

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
        return "mesh" if self._meshReady else "preview"

    # ----------------------------------------------------------------- slots
    def _onTick(self) -> None:
        self._angleY = (self._angleY + self._degreesPerTick) % 360.0
        self._evolutionPhase = (self._evolutionPhase + self._evolutionSpeed) % (2.0 * pi)
        self.update()

    def _onMeshBaked(self, payload: dict) -> None:
        self._pendingBake = payload
        self.update()

    # ---------------------------------------------------------------- OpenGL
    def initializeGL(self) -> None:
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_POINT_SMOOTH)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glShadeModel(GL_SMOOTH)
        # Fully transparent clear — parent window shows through
        glClearColor(0.0, 0.0, 0.0, 0.0)
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
                self._uploadVbos(self._pendingBake)
                self._meshReady = True
            except Exception:
                self._meshReady = False
            self._pendingBake = None

        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0.0, 0.05, -3.15)
        glRotatef(self._angleX, 1.0, 0.0, 0.0)
        glRotatef(self._angleY, 0.0, 1.0, 0.0)

        if self._meshReady:
            self._drawCoreVbo()
            self._drawMeshVbo()
        else:
            self._drawPreviewSphere()

        self._drawENutsLabel()

    # ---------------------------------------------------------------- preview (while baking)
    def _drawPreviewSphere(self, radius: float = 1.0, bands: int = 28) -> None:
        lPhase = self._evolutionPhase
        for lLat in range(bands):
            lTheta1 = lLat * pi / bands
            lTheta2 = (lLat + 1) * pi / bands
            glBegin(GL_QUAD_STRIP)
            for lLon in range(bands + 1):
                lPhi = lLon * 2.0 * pi / bands
                lT = (lLon / bands + 0.1 * sin(lPhase)) % 1.0
                lR = 0.55 * (1.0 - lT) + 0.04 * lT
                lG = 0.12 * (1.0 - lT) + 0.75 * lT
                lB = 0.85 * (1.0 - lT) + 0.95 * lT
                glColor4f(lR * 0.35, lG * 0.35, lB * 0.45, 0.95)
                glVertex3f(*_spherePoint(radius * 0.97, lTheta1, lPhi))
                glVertex3f(*_spherePoint(radius * 0.97, lTheta2, lPhi))
            glEnd()

        glLineWidth(1.2)
        for lLat in range(0, bands, 2):
            lTheta = lLat * pi / bands
            glBegin(GL_LINES)
            for lLon in range(bands):
                lPhi1 = lLon * 2.0 * pi / bands
                lPhi2 = (lLon + 1) * 2.0 * pi / bands
                lT = lLon / bands
                lR = 0.85 * (1.0 - lT) + 0.05 * lT
                lG = 0.20 * (1.0 - lT) + 0.95 * lT
                lB = 0.98
                glColor4f(lR, lG, lB, 0.7)
                glVertex3f(*_spherePoint(radius, lTheta, lPhi1))
                glVertex3f(*_spherePoint(radius, lTheta, lPhi2))
            glEnd()

    # ---------------------------------------------------------------- bake / VBO
    def _startMeshBake(self) -> None:
        if self._worker is not None and self._worker.isRunning():
            return
        self._worker = _MeshBakeWorker(parent=self)
        self._worker.Baked.connect(self._onMeshBaked)
        self._worker.start()

    def _uploadVbos(self, payload: dict) -> None:
        self._coreLon = payload["coreLon"]
        self._lineLon = payload["lineLon"]
        self._nodeLon = payload["nodeLon"]
        self._nodeLat = payload["nodeLat"]
        self._coreCount = int(payload["coreCount"])
        self._lineCount = int(payload["lineCount"])
        self._nodeCount = int(payload["nodeCount"])

        def _bytes(a: array) -> bytes:
            return a.tobytes()

        def _replace(attr: str, data: array) -> int:
            lOld = getattr(self, attr)
            if lOld:
                glDeleteBuffers(1, [lOld])
            lId = int(glGenBuffers(1))
            glBindBuffer(GL_ARRAY_BUFFER, lId)
            glBufferData(GL_ARRAY_BUFFER, _bytes(data), GL_STATIC_DRAW)
            setattr(self, attr, lId)
            return lId

        _replace("_coreVbo", payload["corePos"])
        _replace("_lineVbo", payload["linePos"])
        _replace("_nodeVbo", payload["nodePos"])

        for lAttr in ("_coreColorVbo", "_lineColorVbo", "_nodeColorVbo"):
            lOld = getattr(self, lAttr)
            if lOld:
                glDeleteBuffers(1, [lOld])
            setattr(self, lAttr, int(glGenBuffers(1)))

        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def _lonRgb(self, lonT: float, phase: float) -> tuple[float, float, float]:
        lShift = (lonT + 0.12 * sin(phase)) % 1.0
        lR = 0.85 * (1.0 - lShift) + 0.05 * lShift
        lG = 0.18 * (1.0 - lShift) + 0.95 * lShift
        lB = 0.98 * (1.0 - lShift) + 1.00 * lShift
        return (lR, lG, lB)

    def _fillCoreColors(self) -> bytes:
        lPhase = self._evolutionPhase
        lColors = array("f")
        for lI in range(self._coreCount):
            lLonT = self._coreLon[lI] if lI < len(self._coreLon) else 0.0
            lR, lG, lB = self._lonRgb(lLonT, lPhase)
            lColors.extend((lR * 0.10, lG * 0.12, lB * 0.22 + 0.04, 0.96))
        return lColors.tobytes()

    def _fillLineColors(self) -> bytes:
        lPhase = self._evolutionPhase
        lColors = array("f")
        for lI in range(self._lineCount):
            lLonT = self._lineLon[lI] if lI < len(self._lineLon) else 0.0
            lR, lG, lB = self._lonRgb(lLonT, lPhase)
            lWave = 0.55 + 0.45 * sin(lPhase + lLonT * 2.5 * pi)
            lColors.extend((lR, lG, lB, 0.35 + 0.55 * lWave))
        return lColors.tobytes()

    def _fillNodeColors(self) -> bytes:
        lPhase = self._evolutionPhase
        lColors = array("f")
        for lI in range(self._nodeCount):
            lLonT = self._nodeLon[lI] if lI < len(self._nodeLon) else 0.0
            lLatT = self._nodeLat[lI] if lI < len(self._nodeLat) else 0.5
            lR, lG, lB = self._lonRgb(lLonT, lPhase)
            lPulse = 0.5 + 0.5 * sin(lPhase * 1.6 + lLonT * 5.0 * pi + lLatT * 3.0 * pi)
            lColors.extend(
                (
                    min(lR + 0.3 * lPulse, 1.0),
                    min(lG + 0.3 * lPulse, 1.0),
                    min(lB + 0.2 * lPulse, 1.0),
                    0.5 + 0.5 * lPulse,
                )
            )
        return lColors.tobytes()

    def _drawCoreVbo(self) -> None:
        if self._coreCount <= 0 or not self._coreVbo:
            return
        lColors = self._fillCoreColors()
        glBindBuffer(GL_ARRAY_BUFFER, self._coreColorVbo)
        glBufferData(GL_ARRAY_BUFFER, lColors, GL_DYNAMIC_DRAW)

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        glBindBuffer(GL_ARRAY_BUFFER, self._coreVbo)
        glVertexPointer(3, GL_FLOAT, 0, None)
        glBindBuffer(GL_ARRAY_BUFFER, self._coreColorVbo)
        glColorPointer(4, GL_FLOAT, 0, None)
        glDepthMask(True)
        glDrawArrays(GL_TRIANGLES, 0, self._coreCount)
        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def _drawMeshVbo(self) -> None:
        if self._lineCount <= 0 or not self._lineVbo:
            return

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)

        lLineColors = self._fillLineColors()
        glBindBuffer(GL_ARRAY_BUFFER, self._lineColorVbo)
        glBufferData(GL_ARRAY_BUFFER, lLineColors, GL_DYNAMIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, self._lineVbo)
        glVertexPointer(3, GL_FLOAT, 0, None)
        glBindBuffer(GL_ARRAY_BUFFER, self._lineColorVbo)
        glColorPointer(4, GL_FLOAT, 0, None)
        glLineWidth(1.35)
        glDrawArrays(GL_LINES, 0, self._lineCount)

        if self._nodeCount > 0 and self._nodeVbo:
            lNodeColors = self._fillNodeColors()
            glBindBuffer(GL_ARRAY_BUFFER, self._nodeColorVbo)
            glBufferData(GL_ARRAY_BUFFER, lNodeColors, GL_DYNAMIC_DRAW)
            glBindBuffer(GL_ARRAY_BUFFER, self._nodeVbo)
            glVertexPointer(3, GL_FLOAT, 0, None)
            glBindBuffer(GL_ARRAY_BUFFER, self._nodeColorVbo)
            glColorPointer(4, GL_FLOAT, 0, None)
            glPointSize(3.6)
            glDrawArrays(GL_POINTS, 0, self._nodeCount)

        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # ---------------------------------------------------------------- eNuts label
    def _drawENutsLabel(self) -> None:
        lPainter = QPainter(self)
        lPainter.setRenderHint(QPainter.RenderHint.Antialiasing)
        lPainter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        # Do not fill the widget rect — preserves GL alpha outside the orb/text
        lPainter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)

        lW, lH = self.width(), self.height()
        if lW < 8 or lH < 8:
            lPainter.end()
            return

        lText = "eNuts"
        lPixel = max(18, int(min(lW, lH) * 0.15))
        lFont = QFont("Segoe UI", lPixel, QFont.Weight.Bold)
        lFont.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        lPainter.setFont(lFont)

        lMetrics = lPainter.fontMetrics()
        lTextW = lMetrics.horizontalAdvance(lText)
        lTextH = lMetrics.height()
        lX = (lW - lTextW) / 2.0
        lY = lH * 0.70 + lTextH * 0.28

        lPhase = self._evolutionPhase
        lT = 0.5 + 0.5 * sin(lPhase)
        lT2 = 0.5 + 0.5 * sin(lPhase + 1.7)
        lC0 = QColor(int(170 + 60 * lT), int(140 + 40 * (1 - lT)), int(210 + 30 * lT))
        lC1 = QColor(int(100 + 80 * (1 - lT2)), int(160 + 70 * lT2), int(230))
        lC2 = QColor(int(60 + 40 * (1 - lT)), int(200 + 40 * lT), int(240))

        for lGlow, lAlpha in ((8, 30), (4, 55)):
            lPainter.setPen(QPen(QColor(lC1.red(), lC1.green(), lC1.blue(), lAlpha), lGlow))
            lPainter.drawText(int(lX), int(lY), lText)

        lGrad = QLinearGradient(lX, lY - lTextH, lX + lTextW, lY)
        lGrad.setColorAt(0.0, lC0)
        lGrad.setColorAt(0.45, QColor(230, 235, 245))
        lGrad.setColorAt(0.55, lC1)
        lGrad.setColorAt(1.0, lC2)
        lPainter.setPen(QPen(lGrad, 1))
        lPainter.drawText(int(lX), int(lY), lText)
        lPainter.end()

    def closeEvent(self, event) -> None:
        if self._worker is not None and self._worker.isRunning():
            self._worker.requestInterruption()
            self._worker.wait(400)
        self.makeCurrent()
        for lAttr in (
            "_coreVbo",
            "_coreColorVbo",
            "_lineVbo",
            "_lineColorVbo",
            "_nodeVbo",
            "_nodeColorVbo",
        ):
            lId = getattr(self, lAttr, 0)
            if lId:
                glDeleteBuffers(1, [lId])
                setattr(self, lAttr, 0)
        self.doneCurrent()
        super().closeEvent(event)
