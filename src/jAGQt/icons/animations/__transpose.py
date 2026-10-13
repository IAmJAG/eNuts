# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtCore import QEasingCurve, Qt, QVariantAnimation
from PySide6.QtGui import QIcon, QPainter, QPixmap, QTransform

# ==================================================================================
from ...types.interface.widgets.icons import iIcon
from .__iconAnimation import IconAnimation

# ==================================================================================
QECurveType = QEasingCurve.Type
# ==================================================================================


# ==================================================================================
class IconTransposeAnimation(IconAnimation):
    """Horizontal mirror (transpose) of an icon over time — useful for dock arrows."""

    def __init__(
        self, icon: QIcon,
        iconSize: int = 20, durationMs: int = 160,
        easing: QECurveType = QECurveType.InOutCubic,        
        target: Optional[iIcon] = None,
        *args, **kwargs
    ) -> None:
        super().__init__(
            durationMs=durationMs,
            easing=easing,
            *args, **kwargs
        )
        self._icon: Optional[QIcon] = icon
        self._iconSize: int = max(1, int(iconSize))
        self._animation: Optional[QVariantAnimation] = None
        self.target: Optional[iIcon] = target

    def setIcon(self, icon: QIcon) -> None:
        self._icon = icon

    def setIconSize(self, iconSize: int) -> None:
        self._iconSize = max(1, int(iconSize))

    def _validate(self) -> bool:
        ret = super()._validate()        
        if self._icon is None:
            warning(f"[{self.__class__.__name__}] no valid icons")
            return False

        return True and ret

    def start(self) -> None:        
        if not self._validate():
            self._onFinished()
            return

        duration: int = self._durationMs
        ecurve: QECurveType = self._easing        

        animation: QVariantAnimation = QVariantAnimation(self)
        animation.setDuration(duration)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(ecurve)
        animation.valueChanged.connect(self._onProgress)
        animation.finished.connect(self._onFinished)

        self._animation: Optional[QVariantAnimation] = animation        

        super().start()
        self._animation.start()

    def _onProgress(self, value: object) -> None:
        lT: float = float(value)
        lSize: int = self._iconSize
        lSrc: QPixmap = self._icon.pixmap(lSize, lSize)
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

        self._xapplyPixmap(lFrame)
        super()._onProgress(value)

    def _xapplyPixmap(self, pixmap: QPixmap) -> None:
        if self._target is None: return
        if not isinstance(self._target, iIcon):
            warning(f"[{self.__class__.__name__}] no valid target")
            return        
        self._target.setIcon(pixmap)
    
    def _onFinished(self) -> None:
        self._animation = None
        if self._icon is not None and self._target is not None:
            lMirrored: QPixmap = self._icon.pixmap(self._iconSize, self._iconSize).transformed(
                QTransform().scale(-1, 1)
            )
            self._xapplyPixmap(lMirrored)

        super()._onFinished()

    def stop(self) -> None:
        if self._animation is not None:
            self._animation.stop()
            self._animation = None
        super().stop()


