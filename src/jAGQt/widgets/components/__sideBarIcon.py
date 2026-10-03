# ==================================================================================
# src/jAGQt/widgets/components/__sideBarIcon.py
# ==================================================================================
from typing import Optional, Union

# ==================================================================================
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QLabel, QSizePolicy, QWidget

# ==================================================================================
from jAGQt.types.components import ComponentBase


# ==================================================================================
class SideBarIcon(QLabel, ComponentBase):
    """Independent square icon widget for SideBar items.

    Always maintains a 1:1 aspect ratio. Size is fully configurable.
    """

    def __init__(
        self,
        icon: Optional[Union[QIcon, QPixmap, str]] = None,
        iconSize: int = 24,
        parent: Optional[QWidget] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)

        self.setObjectName("SideBarIcon")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setScaledContents(False)

        self._iconSize: int = max(1, iconSize)
        self._icon: Optional[Union[QIcon, QPixmap]] = None

        self.IconSize = self._iconSize
        if icon is not None:
            self.SetIcon(icon)

    # ================================================================================== public API
    def SetIcon(self, icon: Optional[Union[QIcon, QPixmap, str]]) -> None:
        """Accepts QIcon, QPixmap, or a resource/file path string."""
        if icon is None:
            self._icon = None
            self.clear()
            return

        if isinstance(icon, str):
            lPixmap = QPixmap(icon)
            if lPixmap.isNull():
                lIcon = QIcon(icon)
                self._icon = lIcon if not lIcon.isNull() else None
            else:
                self._icon = lPixmap
        elif isinstance(icon, (QIcon, QPixmap)):
            self._icon = icon
        else:
            self._icon = None

        self._updatePixmap()

    def ClearIcon(self) -> None:
        self.SetIcon(None)

    # ================================================================================== properties
    @property
    def IconSize(self) -> int:
        return self._iconSize

    @IconSize.setter
    def IconSize(self, value: int) -> None:
        lSize = max(1, int(value))
        if lSize == self._iconSize:
            return
        self._iconSize = lSize
        self.setFixedSize(QSize(lSize, lSize))
        self._updatePixmap()

    @property
    def Icon(self) -> Optional[Union[QIcon, QPixmap]]:
        return self._icon

    # ================================================================================== private
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
