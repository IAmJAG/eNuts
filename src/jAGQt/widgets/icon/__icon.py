# ==================================================================================
from typing import Optional, Union

# ==================================================================================
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QLabel

# ==================================================================================
from jAGFx.workflow import workflow

# ==================================================================================
from ..components import ComponentBase


# ==================================================================================
@workflow
class Icon(QLabel, ComponentBase):
    OBJECT_NAME = "W_ICON"

    def __init__(
        self,
        icon: Optional[Union[QIcon, QPixmap, str]] = None,
        background: Optional[Union[str, QColor]] = None,
        foreground: Optional[Union[str, QColor]] = None,
        *args,
        **kwargs,
    ) -> None:
        OBJNAME: str = kwargs.pop("objectName", self.OBJECT_NAME)
        # Do not pass objectName through super: with QLabel + ComponentBase, residual
        # kwargs can reach object.__init__ and raise TypeError.
        super().__init__(*args, **kwargs)
        self.setObjectName(OBJNAME)
        self._icon: Optional[QIcon] = icon
        self._background: QColor = background or QColor(Qt.GlobalColor.transparent)
        self._foreground: QColor = foreground or QColor(Qt.GlobalColor.darkGray)

    def _wInitializeUI(self):
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        background: Optional[Union[str, QColor]] = self._background
        foreground: Optional[Union[str, QColor]] = self._foreground

        if isinstance(background, str):
            self._background = QColor(background)
        elif isinstance(background, QColor):
            self._background = background
        else:
            self._background = QColor(Qt.GlobalColor.transparent)

        if isinstance(foreground, str):
            self._foreground = QColor(foreground)
        elif isinstance(foreground, QColor):
            self._foreground = foreground
        else:
            self._foreground = QColor()

        self._applyStyles()

        if self._icon is not None:
            self.setIcon(self._icon)

    def _applyStyles(self):
        lStyles = []
        if self._background.isValid() and self._background.alpha() > 0:
            lStyles.append(
                f"background-color: {self._background.name(QColor.NameFormat.HexArgb)};"
            )
        else:
            lStyles.append("background-color: transparent;")

        if self._foreground.isValid():
            lStyles.append(
                f"color: {self._foreground.name(QColor.NameFormat.HexArgb)};"
            )

        self.setStyleSheet(" ".join(lStyles))

    def setBackground(self, background: Optional[Union[str, QColor]]):
        if isinstance(background, str):
            self._background = QColor(background)
        elif isinstance(background, QColor):
            self._background = background
        else:
            self._background = QColor(Qt.GlobalColor.transparent)
        self._applyStyles()

    def setForeground(self, foreground: Optional[Union[str, QColor]]):
        if isinstance(foreground, str):
            self._foreground = QColor(foreground)
        elif isinstance(foreground, QColor):
            self._foreground = foreground
        else:
            self._foreground = QColor()
        self._applyStyles()
        if self._icon is not None:
            self._updatePixmap()

    @property
    def iconSize(self) -> int:
        return self.size().height()

    @property
    def icon(self) -> Optional[Union[QIcon, QPixmap]]:
        return self._icon

    def setIcon(self, icon: Optional[Union[QIcon, QPixmap, str]]):
        if icon is None:
            self.clear()
            return

        if isinstance(icon, str):
            icon = QIcon(icon)
        elif isinstance(icon, QPixmap):
            icon = QIcon(icon)

        self._icon = icon
        self._updatePixmap()

    def _updatePixmap(self):
        if self._icon is None:
            super().clear()
            return

        lTargetSize = self.size()
        if (
            lTargetSize.isEmpty()
            or lTargetSize.width() <= 0
            or lTargetSize.height() <= 0
        ):
            lTargetSize = QSize(24, 24)

        lPixmap = self._icon.pixmap(lTargetSize)
        if not lPixmap.isNull():
            if self._foreground.isValid() and self._foreground.alpha() > 0:
                lTintedPixmap = QPixmap(lPixmap.size())
                lTintedPixmap.fill(Qt.GlobalColor.transparent)
                lPainter = QPainter(lTintedPixmap)
                lPainter.drawPixmap(0, 0, lPixmap)
                lPainter.setCompositionMode(
                    QPainter.CompositionMode.CompositionMode_SourceIn
                )
                lPainter.fillRect(lTintedPixmap.rect(), self._foreground)
                lPainter.end()
                lPixmap = lTintedPixmap

            lScaledPixmap = lPixmap.scaled(
                lTargetSize,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            super().setPixmap(lScaledPixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._icon is not None:
            self._updatePixmap()

    def clear(self):
        self._icon = None
        super().clear()
