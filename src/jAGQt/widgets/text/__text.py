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
        self, text: str, elidedMode: EMode = EMode.ElideRight,
        wordWrap: bool = False, *args, **kwargs,
    ) -> None:
        lObjName: str = kwargs.pop("objectName", self.OBJECT_NAME)
        super().__init__(objectName=lObjName, *args, **kwargs)
        self._fullText: str = text
        self._elidedMode: EMode = elidedMode
        self._wordWrap: bool = wordWrap

    def _wInitializeUI(self) -> None:
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setWordWrap(self._wordWrap)
        self._applySizePolicy()
        self.setText(self._fullText)

    def _applySizePolicy(self) -> None:
        # Expand horizontally; never grow vertically unless word-wrap is on
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

    # ==================================================================================
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
        # If word wrap is enabled, let QLabel handle native multi-line wrapping automatically
        if self._wordWrap:
            super().setText(self._fullText)
            self.setVisible(bool(self._fullText.strip()))
            return

        lMetrics: QFontMetrics = QFontMetrics(self.font())
        lAvailableWidth = (
            self.width()
            - self.contentsMargins().left()
            - self.contentsMargins().right()
        )

        text: str = self._fullText
        if lAvailableWidth > 0:
            text = lMetrics.elidedText(text, self._elidedMode, lAvailableWidth)

        super().setText(text)
        self.setVisible(bool(text.strip()))

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._updateTextDisplay()

    def setText(self, text: str) -> None:
        self._fullText = text
        self._updateTextDisplay()
