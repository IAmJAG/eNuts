# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtCore import QEasingCurve, Qt, QVariantAnimation
from PySide6.QtGui import QIcon, QPainter, QPixmap

# ==================================================================================
from ...types.interface.widgets.icons import iIcon
from .__iconAnimation import IconAnimation

# ==================================================================================
QECurveType = QEasingCurve.Type
# ==================================================================================


# ==================================================================================
class IconMorphAnimation(IconAnimation):
    def __init__(
        self, startIcon: Optional[QIcon] = None, endIcon: Optional[QIcon] = None,
        iconSize: int = 20, durationMs: int = 180,
        easing: QECurveType = QECurveType.InOutCubic,
        target: Optional[iIcon] = None,
        *args, **kwargs
    ) -> None:
        super().__init__(
            durationMs=durationMs, easing=easing,
            *args, **kwargs
        )
        self._startIcon: Optional[QIcon] = startIcon
        self._endIcon: Optional[QIcon] = endIcon
        self._iconSize: int = max(1, int(iconSize))
        self._animation: Optional[QVariantAnimation] = None
        self.target: Optional[iIcon] = target        

    def setIcons(self, startIcon: QIcon, endIcon: QIcon) -> None:
        self._startIcon = startIcon
        self._endIcon = endIcon

    def setIconSize(self, iconSize: int) -> None:
        self._iconSize = max(1, int(iconSize))

    def _validate(self) -> None:
        if self._target is None or not isinstance(self._target, iIcon):
            warning(f"[{self.__class__.__name__}] no valid target")
            return False

        if self._startIcon is None or self._endIcon is None:
            warning(f"[{self.__class__.__name__}] no valid icons")
            return False

        return True

    def start(self) -> None:        
        super().start()
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
        self._animation.start()        

    def _onProgress(self, value: object) -> None:
        lT: float = float(value)
        lSize: int = self._iconSize
        lStart: QPixmap = self._startIcon.pixmap(lSize, lSize)
        lEnd: QPixmap = self._endIcon.pixmap(lSize, lSize)
        lFrame: QPixmap = QPixmap(lSize, lSize)
        lFrame.fill(Qt.GlobalColor.transparent)
        lPainter: QPainter = QPainter(lFrame)
        lPainter.setOpacity(1.0 - lT)
        lPainter.drawPixmap(0, 0, lStart)
        lPainter.setOpacity(lT)
        lPainter.drawPixmap(0, 0, lEnd)
        lPainter.end()
        self._xapplyPixmap(lFrame)        
        self.onProgress.emit(value)

    def _onFinished(self) -> None:
        self._animation = None
        if self._endIcon is not None:
            self._applyPixmap(self._endIcon.pixmap(self._iconSize, self._iconSize))

        self.onFinished.emit(self)    

    def stop(self) -> None:
        if self._animation is not None:
            self._animation.stop()
            self._animation = None
        super().stop()    

    def _xapplyPixmap(self, pixmap: QIcon | QPixmap) -> None:
        if self._target is None: return
        if not isinstance(self._target, iIcon):
            warning(f"[{self.__class__.__name__}] no valid target")
            return
        
        self._target.setIcon(pixmap)

    