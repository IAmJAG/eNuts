# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtCore import QEasingCurve, QObject, Qt, QVariantAnimation
from PySide6.QtGui import QIcon, QPainter, QPixmap, QTransform
from PySide6.QtWidgets import QLabel, QWidget

# ==================================================================================
from .__base import IconAnimationBase


# ==================================================================================
class IconTransposeAnimation(IconAnimationBase):
    """Horizontal mirror (transpose) of an icon over time — useful for dock arrows."""

    def __init__(
        self,
        target: Optional[QWidget] = None,
        icon: Optional[QIcon] = None,
        iconSize: int = 20,
        durationMs: int = 160,
        easing: QEasingCurve.Type = QEasingCurve.Type.InOutCubic,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(target=target, durationMs=durationMs, easing=easing, parent=parent)
        self._icon: Optional[QIcon] = icon
        self._iconSize: int = max(1, int(iconSize))
        self._anim: Optional[QVariantAnimation] = None

    def SetIcon(self, icon: QIcon) -> None:
        self._icon = icon

    def SetIconSize(self, iconSize: int) -> None:
        self._iconSize = max(1, int(iconSize))

    def _onStart(self) -> None:
        if self._target is None or self._icon is None:
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
        lSize: int = self._iconSize
        lSrc: QPixmap = self._icon.pixmap(lSize, lSize)
        # Scale X from 1 → 0 → -1 (flip)
        lScaleX: float = 1.0 - 2.0 * lT
        lTransform: QTransform = QTransform()
        lTransform.translate(lSize * 0.5, lSize * 0.5)
        lTransform.scale(lScaleX, 1.0)
        lTransform.translate(-lSize * 0.5, -lSize * 0.5)

        lFrame: QPixmap = QPixmap(lSize, lSize)
        lFrame.fill(Qt.GlobalColor.transparent)
        lPainter: QPainter = QPainter(lFrame)
        lPainter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        lPainter.setTransform(lTransform)
        lPainter.drawPixmap(0, 0, lSrc)
        lPainter.end()

        if isinstance(self._target, QLabel):
            self._target.setPixmap(lFrame)
        elif hasattr(self._target, "setPixmap"):
            self._target.setPixmap(lFrame)

    def _onAnimFinished(self) -> None:
        self._anim = None
        if self._icon is not None and self._target is not None:
            lMirrored: QPixmap = self._icon.pixmap(self._iconSize, self._iconSize).transformed(
                QTransform().scale(-1, 1)
            )
            if isinstance(self._target, QLabel):
                self._target.setPixmap(lMirrored)
            elif hasattr(self._target, "setPixmap"):
                self._target.setPixmap(lMirrored)
        self._emitFinished()
