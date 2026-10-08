# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtCore import QEasingCurve, QObject, QVariantAnimation
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QLabel, QWidget

# ==================================================================================
from .__base import IconAnimationBase


# ==================================================================================
class IconMorphAnimation(IconAnimationBase):
    """Cross-fade morph from one icon to another on a QLabel (or any widget with setPixmap).

    Progress 0 → start icon, 1 → end icon. Intermediate frames blend both pixmaps.
    """

    def __init__(
        self,
        target: Optional[QWidget] = None,
        startIcon: Optional[QIcon] = None,
        endIcon: Optional[QIcon] = None,
        iconSize: int = 20,
        durationMs: int = 180,
        easing: QEasingCurve.Type = QEasingCurve.Type.InOutCubic,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(target=target, durationMs=durationMs, easing=easing, parent=parent)
        self._startIcon: Optional[QIcon] = startIcon
        self._endIcon: Optional[QIcon] = endIcon
        self._iconSize: int = max(1, int(iconSize))
        self._anim: Optional[QVariantAnimation] = None

    def SetIcons(self, startIcon: QIcon, endIcon: QIcon) -> None:
        self._startIcon = startIcon
        self._endIcon = endIcon

    def SetIconSize(self, iconSize: int) -> None:
        self._iconSize = max(1, int(iconSize))

    def _onStart(self) -> None:
        if self._target is None or self._startIcon is None or self._endIcon is None:
            self._emitFinished()
            return

        self._anim = QVariantAnimation(self)
        self._anim.setDuration(self._durationMs)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setEasingCurve(self._easing)
        self._anim.valueChanged.connect(self._onProgress)
        self._anim.finished.connect(self._onAnimFinished)
        self._anim.start()

    def _onStop(self) -> None:
        if self._anim is not None:
            self._anim.stop()
            self._anim = None

    def _onProgress(self, value: object) -> None:
        lT: float = float(value)
        lSize = self._iconSize
        lStart: QPixmap = self._startIcon.pixmap(lSize, lSize)
        lEnd: QPixmap = self._endIcon.pixmap(lSize, lSize)
        lFrame: QPixmap = QPixmap(lSize, lSize)
        lFrame.fill(Qt.GlobalColor.transparent)  # type: ignore[name-defined]

        from PySide6.QtCore import Qt as _Qt

        lFrame.fill(_Qt.GlobalColor.transparent)
        lPainter: QPainter = QPainter(lFrame)
        lPainter.setOpacity(1.0 - lT)
        lPainter.drawPixmap(0, 0, lStart)
        lPainter.setOpacity(lT)
        lPainter.drawPixmap(0, 0, lEnd)
        lPainter.end()

        self._applyPixmap(lFrame)

    def _applyPixmap(self, pixmap: QPixmap) -> None:
        if self._target is None:
            return
        if isinstance(self._target, QLabel):
            self._target.setPixmap(pixmap)
        elif hasattr(self._target, "setPixmap"):
            self._target.setPixmap(pixmap)

    def _onAnimFinished(self) -> None:
        self._anim = None
        if self._endIcon is not None:
            self._applyPixmap(self._endIcon.pixmap(self._iconSize, self._iconSize))
        self._emitFinished()
