# ==================================================================================
# src/eNuts/UI/widgets/__evolvingNeuralBrain.py
# ==================================================================================
from __future__ import annotations

import re
from array import array
from math import cos, pi, sin, sqrt
from typing import Optional

# ==================================================================================
from PySide6.QtCore import Qt, QThread, QTimer, Signal
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
from PySide6.QtWidgets import QApplication, QWidget

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
        GL_LINE_SMOOTH,
        GL_LINES,
        GL_MODELVIEW,
        GL_ONE,
        GL_ONE_MINUS_SRC_ALPHA,
        GL_POINT_SMOOTH,
        GL_POINTS,
        GL_PROJECTION,
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
        "PyOpenGL is required for EvolvingNeuralBrain. "
        "pip install PyOpenGL PyOpenGL-accelerate"
    ) from ex

# ==================================================================================
def _hash01(i: int, j: int = 0) -> float:
    """Deterministic pseudo-noise in [0, 1)."""
    n = (i * 374761393 + j * 668265263) & 0x7FFFFFFF
    n = (n ^ (n >> 13)) * 1274126177
    return ((n ^ (n >> 16)) & 0x7FFFFFFF) / 2147483647.0

def _brainPoint(u: float, v: float, side: float) -> tuple[float, float, float]:
    """Parametric dual-hemisphere brain surface (u lat, v lon, side ±1)."""
    # Base ellipsoid, slightly flattened
    theta = u * pi
    phi = v * 2.0 * pi
    rx, ry, rz = 0.78, 0.62, 0.70

    x = rx * sin(theta) * cos(phi)
    y = ry * cos(theta)
    z = rz * sin(theta) * sin(phi)

    # Split hemispheres along X, leave a shallow medial gap
    x = abs(x) * side + side * 0.06

    # Cortical gyri / sulci via multi-frequency displacement
    n1 = sin(phi * 6.0 + theta * 4.0) * 0.045
    n2 = sin(phi * 11.0 - theta * 7.0) * 0.028
    n3 = cos(phi * 3.5 + theta * 9.0) * 0.022
    bump = 1.0 + n1 + n2 + n3

    # Frontal / occipital elongation
    front = 1.0 + 0.12 * max(0.0, cos(phi))
    top = 1.0 + 0.08 * max(0.0, cos(theta))

    x *= bump * front
    y *= bump * top
    z *= bump

    # Lift slightly so the mass sits above the wordmark
    y += 0.08
    return (x, y, z)

# ==================================================================================
class _BrainBakeWorker(QThread):
    """CPU bake of brain surface + vein polylines."""
    Baked = Signal(object)
    def __init__(self, latBands: int = 28, lonBands: int = 36, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._latBands = latBands
        self._lonBands = lonBands

    def run(self) -> None:
        if self.isInterruptionRequested(): return

        lSurfPos = array("f")
        lSurfNormHint = array("f")  # store (u,v,side) as attributes for shading
        lLatN = self._latBands
        lLonN = self._lonBands

        for side in (-1.0, 1.0):
            for i in range(lLatN):
                if self.isInterruptionRequested():
                    return
                u0 = i / lLatN
                u1 = (i + 1) / lLatN
                for j in range(lLonN):
                    v0 = j / lLonN
                    v1 = (j + 1) / lLonN
                    p00 = _brainPoint(u0, v0, side)
                    p10 = _brainPoint(u1, v0, side)
                    p01 = _brainPoint(u0, v1, side)
                    p11 = _brainPoint(u1, v1, side)
                    for p, u, v in (
                        (p00, u0, v0),
                        (p10, u1, v0),
                        (p01, u0, v1),
                        (p10, u1, v0),
                        (p11, u1, v1),
                        (p01, u0, v1),
                    ):
                        lSurfPos.extend(p)
                        lSurfNormHint.extend((u, v, side))

        # Vein network: several branching meridians + cross links per hemisphere
        lVeinPos = array("f")
        lVeinParam = array("f")  # phase parameter along path [0,1]

        def _addVein(points: list[tuple[float, float, float]]) -> None:
            n = len(points)
            if n < 2:
                return
            for k in range(n - 1):
                lVeinPos.extend(points[k])
                lVeinPos.extend(points[k + 1])
                t0 = k / max(n - 1, 1)
                t1 = (k + 1) / max(n - 1, 1)
                lVeinParam.append(t0)
                lVeinParam.append(t1)

        for side in (-1.0, 1.0):
            for seed in range(7):
                if self.isInterruptionRequested():
                    return
                baseV = (seed + 0.35) / 7.0
                pts: list[tuple[float, float, float]] = []
                steps = 18
                for s in range(steps + 1):
                    u = 0.12 + 0.76 * (s / steps)
                    wobble = 0.04 * sin(s * 0.9 + seed)
                    v = (baseV + wobble) % 1.0
                    pts.append(_brainPoint(u, v, side))
                _addVein(pts)

                # Side branch
                if seed % 2 == 0:
                    mid = steps // 2
                    branch: list[tuple[float, float, float]] = [pts[mid]]
                    for b in range(1, 8):
                        u = 0.12 + 0.76 * ((mid + b * 0.4) / steps)
                        v = (baseV + 0.08 * b) % 1.0
                        branch.append(_brainPoint(min(u, 0.95), v, side))
                    _addVein(branch)

            # Cross-hemisphere hint near the stem
            cross: list[tuple[float, float, float]] = []
            for s in range(10):
                t = s / 9.0
                u = 0.72 + 0.12 * sin(t * pi)
                v = 0.5
                # blend sides toward midline
                pL = _brainPoint(u, v, -1.0)
                pR = _brainPoint(u, v, 1.0)
                cross.append(
                    (
                        pL[0] * (1 - t) + pR[0] * t,
                        pL[1] * (1 - t) + pR[1] * t,
                        pL[2] * (1 - t) + pR[2] * t,
                    )
                )
            _addVein(cross)

        self.Baked.emit(
            {
                "surfPos": lSurfPos,
                "surfAttr": lSurfNormHint,
                "surfCount": len(lSurfPos) // 3,
                "veinPos": lVeinPos,
                "veinParam": lVeinParam,
                "veinCount": len(lVeinPos) // 3,
            }
        )

# ==================================================================================
class EvolvingNeuralBrain(QOpenGLWidget):
    """
        Realistic dual-hemisphere brain with pulsing veins and chrome eNuts.

        Background clear color follows the applied application stylesheet theme.
    """
    def __init__(
        self, parent: Optional[QWidget] = None, *, revolutionMs: int = 16,
        degreesPerTick: float = 0.22, evolutionSpeed: float = 0.035,
    ) -> None:
        lFmt = QSurfaceFormat()
        lFmt.setSamples(4)
        lFmt.setAlphaBufferSize(8)
        lFmt.setDepthBufferSize(24)
        lFmt.setSwapBehavior(QSurfaceFormat.SwapBehavior.DoubleBuffer)
        lFmt.setRenderableType(QSurfaceFormat.RenderableType.OpenGL)

        super().__init__(parent)
        self.setObjectName("EvolvingNeuralBrain")
        self.setFormat(lFmt)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)
        self.setAutoFillBackground(False)
        self.setStyleSheet("background: transparent; border: none;")

        self._angleY = 0.0
        self._angleX = 12.0
        self._degreesPerTick = degreesPerTick
        self._evolutionPhase = 0.0
        self._evolutionSpeed = evolutionSpeed

        self._meshReady = False
        self._pendingBake: Optional[dict] = None
        self._worker: Optional[_BrainBakeWorker] = None

        self._surfVbo = self._surfColorVbo = 0
        self._veinVbo = self._veinColorVbo = 0
        self._surfCount = self._veinCount = 0
        self._surfAttr: array = array("f")
        self._veinParam: array = array("f")

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._onTick)
        self._timer.start(revolutionMs)

        self.setMinimumSize(200, 200)

    # ------------------------------------------------------------------ public
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

    # ----------------------------------------------------------------- slots
    def _onTick(self) -> None:
        self._angleY = (self._angleY + self._degreesPerTick) % 360.0
        self._evolutionPhase = (self._evolutionPhase + self._evolutionSpeed) % (2.0 * pi)
        self.update()

    def _onBaked(self, payload: dict) -> None:
        self._pendingBake = payload
        self.update()

    # ---------------------------------------------------------------- theme clear
    @staticmethod
    def _parseCssColor(token: str) -> QColor | None:
        t = token.strip().lower()
        if not t:
            return None
        if t == "transparent":
            return QColor(0, 0, 0, 0)
        c = QColor(t)
        return c if c.isValid() else None

    @classmethod
    def _backgroundFromStylesheet(cls, qss: str) -> QColor | None:
        if not qss:
            return None
        patterns = [
            re.compile(r"QMainWindow(?:\s*,\s*QWidget)?\s*\{([^}]*)\}", re.I | re.S),
            re.compile(r"QWidget\s*\{([^}]*)\}", re.I | re.S),
        ]
        bgRe = re.compile(r"background(?:-color)?\s*:\s*([^;{}]+)", re.I)
        for pat in patterns:
            for m in pat.finditer(qss):
                bg = bgRe.search(m.group(1))
                if bg:
                    c = cls._parseCssColor(bg.group(1))
                    if c is not None:
                        return c
        bg = bgRe.search(qss)
        return cls._parseCssColor(bg.group(1)) if bg else None

    def _hostClearColor(self) -> tuple[float, float, float, float]:
        app = QApplication.instance()
        qss = (app.styleSheet() or "") if app is not None else ""
        color = self._backgroundFromStylesheet(qss)
        if color is None:
            host = self.parentWidget() or self.window()
            if host is not None:
                color = host.palette().color(QPalette.ColorRole.Window)
        if color is None or not color.isValid():
            return (0x18 / 255.0, 0x18 / 255.0, 0x18 / 255.0, 1.0)
        if color.alpha() == 0:
            return (0.0, 0.0, 0.0, 0.0)
        return (color.redF(), color.greenF(), color.blueF(), color.alphaF())

    def _applyClearColor(self) -> None:
        r, g, b, a = self._hostClearColor()
        glClearColor(r, g, b, a)

    # ---------------------------------------------------------------- GL
    def initializeGL(self) -> None:
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_POINT_SMOOTH)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glShadeModel(GL_SMOOTH)
        self._applyClearColor()
        self._startBake()

    def resizeGL(self, w: int, h: int) -> None:
        glViewport(0, 0, max(w, 1), max(h, 1))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(34.0, max(w, 1) / max(h, 1), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self) -> None:
        if self._pendingBake is not None:
            try:
                self._upload(self._pendingBake)
                self._meshReady = True
            except Exception:
                self._meshReady = False
            self._pendingBake = None

        self._applyClearColor()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        # Brain slightly above center; room for chrome wordmark just below
        glTranslatef(0.0, 0.28, -3.55)
        glRotatef(self._angleX, 1.0, 0.0, 0.0)
        glRotatef(self._angleY, 0.0, 1.0, 0.0)

        if self._meshReady:
            self._drawSurface()
            self._drawVeins()
        else:
            self._drawPreview()

        self._drawChromeENuts()

    # ---------------------------------------------------------------- bake
    def _startBake(self) -> None:
        if self._worker is not None and self._worker.isRunning():
            return
        self._worker = _BrainBakeWorker(parent=self)
        self._worker.Baked.connect(self._onBaked)
        self._worker.start()

    def _upload(self, payload: dict) -> None:
        self._surfAttr = payload["surfAttr"]
        self._veinParam = payload["veinParam"]
        self._surfCount = int(payload["surfCount"])
        self._veinCount = int(payload["veinCount"])

        def _replace(attr: str, data: array) -> None:
            old = getattr(self, attr)
            if old:
                glDeleteBuffers(1, [old])
            vid = int(glGenBuffers(1))
            glBindBuffer(GL_ARRAY_BUFFER, vid)
            glBufferData(GL_ARRAY_BUFFER, data.tobytes(), GL_STATIC_DRAW)
            setattr(self, attr, vid)

        _replace("_surfVbo", payload["surfPos"])
        _replace("_veinVbo", payload["veinPos"])
        for a in ("_surfColorVbo", "_veinColorVbo"):
            old = getattr(self, a)
            if old:
                glDeleteBuffers(1, [old])
            setattr(self, a, int(glGenBuffers(1)))
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def _fillSurfaceColors(self) -> bytes:
        phase = self._evolutionPhase
        colors = array("f")
        n = self._surfCount
        for i in range(n):
            base = i * 3
            u = self._surfAttr[base] if base < len(self._surfAttr) else 0.5
            v = self._surfAttr[base + 1] if base + 1 < len(self._surfAttr) else 0.5
            # Flesh tone with cool evolutionary tint
            pulse = 0.55 + 0.45 * sin(phase * 1.3 + u * 5.0 + v * 3.0)
            r = 0.55 + 0.12 * pulse + 0.08 * sin(v * 6.0)
            g = 0.32 + 0.10 * pulse
            b = 0.38 + 0.22 * pulse + 0.10 * cos(u * 4.0 + phase)
            colors.extend((min(r, 1.0), min(g, 1.0), min(b, 1.0), 0.98))
        return colors.tobytes()

    def _fillVeinColors(self) -> bytes:
        phase = self._evolutionPhase
        colors = array("f")
        n = self._veinCount
        for i in range(n):
            t = self._veinParam[i] if i < len(self._veinParam) else 0.0
            # Traveling pulse along the vein
            wave = 0.5 + 0.5 * sin(phase * 2.4 - t * 8.0 * pi)
            hot = wave ** 2
            r = 0.55 + 0.40 * hot
            g = 0.05 + 0.15 * hot
            b = 0.12 + 0.55 * hot
            a = 0.35 + 0.60 * hot
            colors.extend((r, g, b, a))
        return colors.tobytes()

    def _drawSurface(self) -> None:
        if self._surfCount <= 0 or not self._surfVbo:
            return
        cols = self._fillSurfaceColors()
        glBindBuffer(GL_ARRAY_BUFFER, self._surfColorVbo)
        glBufferData(GL_ARRAY_BUFFER, cols, GL_DYNAMIC_DRAW)
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        glBindBuffer(GL_ARRAY_BUFFER, self._surfVbo)
        glVertexPointer(3, GL_FLOAT, 0, None)
        glBindBuffer(GL_ARRAY_BUFFER, self._surfColorVbo)
        glColorPointer(4, GL_FLOAT, 0, None)
        glDepthMask(True)
        glDrawArrays(GL_TRIANGLES, 0, self._surfCount)
        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def _drawVeins(self) -> None:
        if self._veinCount <= 0 or not self._veinVbo:
            return
        cols = self._fillVeinColors()
        glBindBuffer(GL_ARRAY_BUFFER, self._veinColorVbo)
        glBufferData(GL_ARRAY_BUFFER, cols, GL_DYNAMIC_DRAW)
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        glBindBuffer(GL_ARRAY_BUFFER, self._veinVbo)
        glVertexPointer(3, GL_FLOAT, 0, None)
        glBindBuffer(GL_ARRAY_BUFFER, self._veinColorVbo)
        glColorPointer(4, GL_FLOAT, 0, None)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glLineWidth(2.2)
        glDrawArrays(GL_LINES, 0, self._veinCount)
        glPointSize(3.0)
        glDrawArrays(GL_POINTS, 0, self._veinCount)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def _drawPreview(self) -> None:
        """Lightweight placeholder while baking."""
        for side in (-1.0, 1.0):
            for i in range(12):
                u0, u1 = i / 12, (i + 1) / 12
                glBegin(GL_TRIANGLES)
                for j in range(16):
                    v0, v1 = j / 16, (j + 1) / 16
                    for p in (
                        _brainPoint(u0, v0, side),
                        _brainPoint(u1, v0, side),
                        _brainPoint(u0, v1, side),
                    ):
                        glColor4f(0.55, 0.35, 0.40, 0.95)
                        glVertex3f(*p)
                glEnd()

    # ---------------------------------------------------------------- chrome eNuts
    def _drawChromeENuts(self) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)

        w, h = self.width(), self.height()
        if w < 8 or h < 8:
            painter.end()
            return

        text = "eNuts"
        # Larger wordmark, short gap under the brain
        pixel = max(22, int(min(w, h) * 0.12))
        font = QFont("Segoe UI", pixel, QFont.Weight.Bold)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        painter.setFont(font)

        metrics = painter.fontMetrics()
        textW = metrics.horizontalAdvance(text)
        textH = metrics.height()
        x = (w - textW) / 2.0
        # Close under the brain mass
        y = h * 0.78 + textH * 0.15

        phase = self._evolutionPhase
        pulse = 0.5 + 0.5 * sin(phase * 1.8)

        # Dark-blue chrome stack: deep shadow → mid bevel → bright ridge → pulse glow
        layers = [
            (4, 0, QColor(5, 10, 28, 160)),
            (2, -1, QColor(15, 35, 90, 200)),
            (1, -2, QColor(30, 70, 150, 220)),
            (0, -3, QColor(80, 140, 220, int(180 + 60 * pulse))),
        ]
        for dx, dy, col in layers:
            painter.setPen(QPen(col, 1))
            painter.drawText(int(x + dx), int(y + dy), text)

        # Main fill — animated dark-blue chrome gradient
        grad = QLinearGradient(x, y - textH, x + textW, y)
        cDeep = QColor(8, 20, 55)
        cMid = QColor(25, 55, 120)
        cHi = QColor(
            int(90 + 50 * pulse),
            int(150 + 40 * pulse),
            int(220 + 20 * pulse),
        )
        cEdge = QColor(12, 30, 70)
        grad.setColorAt(0.0, cDeep)
        grad.setColorAt(0.35, cMid)
        grad.setColorAt(0.55, cHi)
        grad.setColorAt(0.75, cMid)
        grad.setColorAt(1.0, cEdge)
        painter.setPen(QPen(grad, 1))
        painter.drawText(int(x), int(y), text)

        # Specular dash across the glyphs
        spec = QLinearGradient(x, y - textH * 0.6, x + textW, y - textH * 0.2)
        spec.setColorAt(0.0, QColor(255, 255, 255, 0))
        spec.setColorAt(0.45, QColor(200, 230, 255, int(40 + 50 * pulse)))
        spec.setColorAt(0.55, QColor(255, 255, 255, int(70 + 60 * pulse)))
        spec.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setPen(QPen(spec, 1))
        painter.drawText(int(x), int(y - 1), text)

        painter.end()

    def closeEvent(self, event) -> None:
        if self._worker is not None and self._worker.isRunning():
            self._worker.requestInterruption()
            self._worker.wait(400)
        self.makeCurrent()
        for attr in ("_surfVbo", "_surfColorVbo", "_veinVbo", "_veinColorVbo"):
            vid = getattr(self, attr, 0)
            if vid:
                glDeleteBuffers(1, [vid])
                setattr(self, attr, 0)
        self.doneCurrent()
        super().closeEvent(event)
