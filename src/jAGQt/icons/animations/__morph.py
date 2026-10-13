# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional, Union

# ==================================================================================
from PySide6.QtCore import QEasingCurve, Qt, QVariantAnimation
from PySide6.QtGui import QIcon, QPainter, QPixmap

# ==================================================================================
from jAGFx.logging import warning

# ==================================================================================
from ...types.interface.widgets.icons import iIcon
from .__iconAnimation import IconAnimation

# ==================================================================================
QECurveType = QEasingCurve.Type
IconLike = Optional[Union[QIcon, QPixmap, str]]
# ==================================================================================


# ==================================================================================
def _toPixmap(icon: IconLike, size: int) -> QPixmap:
    if icon is None:
        lEmpty = QPixmap(size, size)
        lEmpty.fill(Qt.GlobalColor.transparent)
        return lEmpty
    if isinstance(icon, QPixmap):
        if icon.width() == size and icon.height() == size:
            return icon
        return icon.scaled(
            size,
            size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
    if isinstance(icon, str):
        icon = QIcon(icon)
    if isinstance(icon, QIcon):
        lPm = icon.pixmap(size, size)
        if lPm.isNull():
            lEmpty = QPixmap(size, size)
            lEmpty.fill(Qt.GlobalColor.transparent)
            return lEmpty
        return lPm
    lEmpty = QPixmap(size, size)
    lEmpty.fill(Qt.GlobalColor.transparent)
    return lEmpty


# ==================================================================================
class IconMorphAnimation(IconAnimation):
    def __init__(
        self,
        startIcon: IconLike = None,
        endIcon: IconLike = None,
        iconSize: int = 20,
        durationMs: int = 180,
        easing: QECurveType = QECurveType.InOutCubic,
        target: Optional[iIcon] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(durationMs=durationMs, easing=easing, *args, **kwargs)
        self._startIcon: IconLike = startIcon
        self._endIcon: IconLike = endIcon
        self._iconSize: int = max(1, int(iconSize))
        self._animation: Optional[QVariantAnimation] = None
        if target is not None:
            self.target = target

    def setIcons(self, startIcon: IconLike, endIcon: IconLike) -> None:
        self._startIcon = startIcon
        self._endIcon = endIcon

    def setIconSize(self, iconSize: int) -> None:
        self._iconSize = max(1, int(iconSize))

    def _validate(self) -> bool:
        ret: bool = super()._validate()
        if self._startIcon is None or self._endIcon is None:
            warning(f"[{self.__class__.__name__}] no valid icons")
            return False
        return bool(ret)

    def start(self) -> None:
        if not self._validate():
            # Snap to end without assuming QIcon API
            if self._endIcon is not None:
                self._xapplyPixmap(_toPixmap(self._endIcon, self._iconSize))
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

        self._animation = animation

        super().start()
        self._animation.start()

    def _onProgress(self, value: object) -> None:
        lT: float = float(value)
        lSize: int = self._iconSize
        lStart: QPixmap = _toPixmap(self._startIcon, lSize)
        lEnd: QPixmap = _toPixmap(self._endIcon, lSize)
        lFrame: QPixmap = QPixmap(lSize, lSize)
        lFrame.fill(Qt.GlobalColor.transparent)
        lPainter: QPainter = QPainter(lFrame)
        lPainter.setOpacity(1.0 - lT)
        lPainter.drawPixmap(0, 0, lStart)
        lPainter.setOpacity(lT)
        lPainter.drawPixmap(0, 0, lEnd)
        lPainter.end()
        self._xapplyPixmap(lFrame)
        super()._onProgress(lT)

    def _onFinished(self) -> None:
        self._animation = None
        if self._endIcon is not None:
            self._xapplyPixmap(_toPixmap(self._endIcon, self._iconSize))
        super()._onFinished()

    def stop(self) -> None:
        if self._animation is not None:
            self._animation.stop()
            self._animation = None
        super().stop()

    def _xapplyPixmap(self, pixmap: Union[QIcon, QPixmap]) -> None:
        if self._target is None:
            return
        if not isinstance(self._target, iIcon):
            warning(f"[{self.__class__.__name__}] no valid target")
            return

        # Prefer frame apply so StatefullIcon does not restart the morph.
        lApply = getattr(self._target, "applyFrame", None)
        if callable(lApply):
            lApply(pixmap)
        else:
            self._target.setIcon(pixmap)
