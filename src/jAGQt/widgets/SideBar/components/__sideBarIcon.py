# ==================================================================================
from typing import Optional, Union

# ==================================================================================
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QLabel, QSizePolicy

# ==================================================================================
from jAGFx.workflow import workflow

# ==================================================================================
from ...components import ComponentBase

# ==================================================================================
QPolicy = QSizePolicy.Policy
# ==================================================================================

# ==================================================================================
@workflow
class SideBarIcon(QLabel, ComponentBase):
    OBJECT_NAME = "W_SIDEBAR_ICON"
    def __init__(
        self, icon: Optional[Union[QIcon, QPixmap, str]] = None,
        iconSize: int = 24, *args, **kwargs
    ) -> None:        
        OBJNAME: str = kwargs.pop("objectName", self.OBJECT_NAME)
        super().__init__(objectName=OBJNAME, *args, **kwargs)
        self._icon: Optional[Union[QIcon, QPixmap]] = icon
        self._iconSize: int = iconSize


    def _wInitializeUI(self):
        iconSize: int = self._iconSize
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QPolicy.Fixed, QPolicy.Fixed)
        self.setScaledContents(False)
        self.setFixedSize(QSize(iconSize, iconSize))

    # ================================================================================== 
    def setIcon(self, icon: Optional[Union[QIcon, QPixmap, str]]):
        if icon is None:
            self._icon = None
            self.clear()
            return

        self._icon = None
        if isinstance(icon, str):
            pixmap: QPixmap = QPixmap(icon)
            if pixmap.isNull():
                icon: QIcon = QIcon(icon)
                self._icon = icon if not icon.isNull() else None

            else:
                self._icon = pixmap

        elif isinstance(icon, (QIcon, QPixmap)):
            self._icon = icon

        self._updatePixmap()

    # ==================================================================================
    @property
    def iconSize(self) -> int:
        return self._iconSize

    @iconSize.setter
    def iconSize(self, value: int) -> None:
        size = max(1, int(value))
        if size == self._iconSize: return
        self._iconSize = size
        self.setFixedSize(QSize(size, size))
        self._updatePixmap()

    @property
    def icon(self) -> Optional[Union[QIcon, QPixmap]]:
        return self._icon

    # ==================================================================================
    def _updatePixmap(self) -> None:
        if self._icon is None:
            self.clear()
            return

        iconSize: int = self._iconSize
        target = QSize(iconSize, iconSize)
        if isinstance(self._icon, QIcon):
            pixmap = self._icon.pixmap(target)

        else:
            pixmap = self._icon.scaled(
                target,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )

        self.setPixmap(pixmap)
