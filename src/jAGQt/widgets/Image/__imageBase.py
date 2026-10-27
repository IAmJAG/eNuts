# ==================================================================================
# src/jAGQt/widgets/Image/__imageBase.py
# ==================================================================================
import os
from typing import Optional, Union

# ==================================================================================
from PySide6.QtCore import QRect
from PySide6.QtGui import QColor, QImage, QPixmap

# ==================================================================================
from .__fitMode import ImageFitMode

# ==================================================================================
BACKGROUND_COLOR = QColor("lightgray")
# ==================================================================================

# ==================================================================================
class ImageBase:
    def _wInitializeBase(self) -> None:
        self._image: Optional[QPixmap] = None
        self._drawRect: QRect = QRect()
        self._dirty: bool = True
        
        bg: Union[str, QColor] = self._backgroundColor        
        self.setBackgroundColor(bg)

    # ------------------------------------------------------------------
    # PROPERTIES
    # ------------------------------------------------------------------
    @property
    def fitMode(self) -> ImageFitMode:
        return self._fitMode

    @fitMode.setter
    def fitMode(self, value: ImageFitMode) -> None:
        if value is self._fitMode: return
        self._fitMode = value
        self._markDirty()

    @property
    def image(self) -> Optional[QPixmap]:
        return self._image

    @image.setter
    def image(self, value: Union[QPixmap, QImage, str, None]) -> None:
        if value is None:
            self._image = None
            self._onImageCleared()
            self._markDirty()
            return

        lPixmap = self._toPixmap(value)
        if lPixmap is None or lPixmap.isNull():
            return

        self._image = lPixmap.copy()
        self._onImageSet()
        self._markDirty()

    # ------------------------------------------------------------------
    def setBackgroundColor(self, color: Union[str, QColor]) -> None:
        self._backgroundColor = QColor(color) if isinstance(color, str) else color
        self.update()  # type: ignore[attr-defined]

    # ------------------------------------------------------------------
    # HOOKS (override in subclass)
    # ------------------------------------------------------------------
    def _onImageCleared(self) -> None:
        """Called when image is set to None. Clear subclass buffers."""
        self._drawRect = QRect()

    def _onImageSet(self) -> None:
        """Called after a new image is stored."""
        pass

    def _markDirty(self) -> None:
        self._dirty = True
        self.update()  # type: ignore[attr-defined]

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------
    @staticmethod
    def _toPixmap(value: Union[QPixmap, QImage, str]) -> Optional[QPixmap]:
        if isinstance(value, str):
            if not os.path.exists(value):
                return None
            return QPixmap(value)
        if isinstance(value, QImage):
            return QPixmap.fromImage(value)
        if isinstance(value, QPixmap):
            return value
        raise TypeError("Expected str | QImage | QPixmap | None")
