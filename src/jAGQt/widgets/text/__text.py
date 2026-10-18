# ==================================================================================
from __future__ import annotations

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtGui import QFontMetrics, QResizeEvent
from PySide6.QtWidgets import QLabel, QSizePolicy

# ==================================================================================
from jAGFx.workflow import workflow

# ==================================================================================
from ..components import ComponentBase

# ==================================================================================
EMode = Qt.TextElideMode
QPolicy = QSizePolicy.Policy
# ==================================================================================


# ==================================================================================
@workflow
class Text(QLabel, ComponentBase):
    OBJECT_NAME = "W_TEXT"

    def __init__(
        self,
        text: str,
        elidedMode: EMode = EMode.ElideRight,
        wordWrap: bool = False,
        *args,
        **kwargs,
    ) -> None:
        lObjName: str = kwargs.pop("objectName", self.OBJECT_NAME)
        super().__init__(*args, **kwargs)
        self.setObjectName(lObjName)
        self._fullText: str = text
        self._elidedMode: EMode = elidedMode
        self._wordWrap: bool = wordWrap

    def _wInitializeUI(self) -> None:
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setWordWrap(self._wordWrap)
        self._applySizePolicy()
        self.setText(self._fullText)

    def _applySizePolicy(self) -> None:
        if self._wordWrap:
            self.setSizePolicy(QPolicy.Expanding, QPolicy.Preferred)
        else:
            self.setSizePolicy(QPolicy.Expanding, QPolicy.Fixed)

    @property
    def WordWrap(self) -> bool:
        return self._wordWrap

    @WordWrap.setter
    def WordWrap(self, value: bool) -> None:
        self._wordWrap = value
        self.setWordWrap(value)
        self._applySizePolicy()
        self._updateTextDisplay()

    @property
    def ElidedMode(self) -> EMode:
        return self._elidedMode

    @ElidedMode.setter
    def ElidedMode(self, value: EMode) -> None:
        self._elidedMode = value
        self._updateTextDisplay()

    @property
    def Text(self) -> str:
        return self._fullText

    @Text.setter
    def Text(self, value: str) -> None:
        self._fullText = value
        self._updateTextDisplay()

    def _updateTextDisplay(self) -> None:
        # Visibility follows the *source* string, never the elided result.
        # Width 0 (pre-layout) must not hide or elide away the caption.
        hasText = bool(self._fullText and self._fullText.strip())
        if self._wordWrap:
            super().setText(self._fullText)
            self.setVisible(hasText)
            return

        lAvailableWidth = (
            self.width()
            - self.contentsMargins().left()
            - self.contentsMargins().right()
        )

        if lAvailableWidth <= 0:
            super().setText(self._fullText)
        else:
            lMetrics: QFontMetrics = QFontMetrics(self.font())
            super().setText(
                lMetrics.elidedText(self._fullText, self._elidedMode, lAvailableWidth)
            )
        self.setVisible(hasText)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._updateTextDisplay()

    def setText(self, text: str) -> None:
        self._fullText = text
        self._updateTextDisplay()
