# ==================================================================================
# src/jAGQt/animations/__sizeAnimationBase.py
# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtCore import QRect, QSize
from PySide6.QtWidgets import QWidget

# ==================================================================================
from jAGQt.utilities import AnimationError

# ==================================================================================
from .__animationBase import AnimationBase


# ==================================================================================
class SizeAnimationBase(AnimationBase):
    """Animate a QWidget's size/geometry (not pixmap content).

    Subclasses set ``_startSize`` / ``_endSize`` in ``_onStart`` and implement
    how intermediate sizes are derived in ``_sizeAt(progress)`` (optional override).
    """

    def __init__(self, target: QWidget, *args, **kwargs) -> None:
        if target is None:
            raise AnimationError("Size animation target must not be None")
        if not isinstance(target, QWidget):
            raise AnimationError(
                f"Size animation target must be a QWidget, got {type(target).__name__}"
            )
        super().__init__(*args, **kwargs)
        self._target: QWidget = target
        self._startSize: QSize = QSize()
        self._endSize: QSize = QSize()
        self._startGeo: QRect = QRect()
        self._anchorRight: bool = False
        self._anchorBottom: bool = False

    @property
    def target(self) -> QWidget:
        return self._target

    def _captureStart(self) -> None:
        self._startGeo = QRect(self._target.geometry())
        self._startSize = QSize(self._target.width(), self._target.height())

    def _sizeAt(self, progress: float) -> QSize:
        progress = max(0.0, min(1.0, progress))
        sw, sh = self._startSize.width(), self._startSize.height()
        ew, eh = self._endSize.width(), self._endSize.height()
        w = int(round(sw + (ew - sw) * progress))
        h = int(round(sh + (eh - sh) * progress))
        return QSize(max(0, w), max(0, h))

    def _applySize(self, size: QSize) -> None:
        w = max(0, size.width())
        h = max(0, size.height())
        geo = QRect(self._startGeo)
        if self._anchorRight:
            geo.setX(self._startGeo.right() + 1 - w)
        if self._anchorBottom:
            geo.setY(self._startGeo.bottom() + 1 - h)
        geo.setWidth(w)
        geo.setHeight(h)

        # Prefer fixed size when the widget is on a fixed-size policy path
        # (e.g. SideBar); still update geometry for anchored edges.
        self._target.setFixedSize(w, h)
        if self._anchorRight or self._anchorBottom:
            self._target.setGeometry(geo)
        self._target.updateGeometry()

    def _onProgress(self, progress: float) -> None:
        self._applySize(self._sizeAt(progress))

    def _onFinished(self) -> None:
        self._applySize(self._endSize)
