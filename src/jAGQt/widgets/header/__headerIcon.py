# ==================================================================================
# src/jAGQt/widgets/header/__headerIcon.py
# ==================================================================================
from typing import Optional, Union

# ==================================================================================
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QLabel, QSizePolicy

# ==================================================================================
IconType = Optional[Union[QIcon, QPixmap, str]]
Policy = QSizePolicy.Policy


# ==================================================================================
class _headerIcon(QLabel):
    """Fixed square icon label used inside Header."""

    def __init__(
        self, icon: IconType = None, iconSize: int = 24, *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(Policy.Fixed, Policy.Fixed)
        self.setScaledContents(False)
        self._iconSize: int = max(1, int(iconSize))
        self._icon: Optional[Union[QIcon, QPixmap]] = None
        self.setFixedSize(QSize(self._iconSize, self._iconSize))
        if icon is not None:
            self.SetIcon(icon)

    def SetIcon(self, icon: IconType) -> None:
        if icon is None:
            self._icon = None
            self.clear()
            self.hide()
            return

        if isinstance(icon, str):
            lPixmap = QPixmap(icon)
            if not lPixmap.isNull():
                self._icon = lPixmap
            else:
                lIcon = QIcon(icon)
                self._icon = lIcon if not lIcon.isNull() else None
        elif isinstance(icon, (QIcon, QPixmap)):
            self._icon = icon
        else:
            self._icon = None

        self._updatePixmap()
        self.setVisible(self._icon is not None)

    def SetIconSize(self, iconSize: int) -> None:
        lSize: int = max(1, int(iconSize))
        if lSize == self._iconSize:
            return
        self._iconSize = lSize
        self.setFixedSize(QSize(lSize, lSize))
        self._updatePixmap()

    @property
    def HasIcon(self) -> bool:
        return self._icon is not None

    def _updatePixmap(self) -> None:
        if self._icon is None:
            self.clear()
            return
        lTarget = QSize(self._iconSize, self._iconSize)
        if isinstance(self._icon, QIcon):
            lPixmap = self._icon.pixmap(lTarget)
        else:
            lPixmap = self._icon.scaled(
                lTarget,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        self.setPixmap(lPixmap)
