# ==================================================================================
# src/jAGQt/widgets/components/__sideBarText.py
# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QSizePolicy, QWidget

# ==================================================================================
from jAGQt.types.components import ComponentBase


# ==================================================================================
class SideBarText(QLabel, ComponentBase):
    """Independent text label for SideBar items.

    Fully configurable alignment, elide mode, and visibility.
    """

    def __init__(
        self, text: str = "",
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
        elideMode: Qt.TextElideMode = Qt.TextElideMode.ElideRight, parent: Optional[QWidget] = None,
        *args, **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)

        self.setObjectName("SideBarText")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setWordWrap(False)

        self._elideMode: Qt.TextElideMode = elideMode
        self._rawText: str = text

        self.Alignment = alignment
        self.Text = text

    # ================================================================================== public API
    def SetText(self, text: str) -> None:
        self.Text = text

    def ClearText(self) -> None:
        self.Text = ""

    # ================================================================================== properties
    @property
    def Text(self) -> str:
        return self._rawText

    @Text.setter
    def Text(self, value: str) -> None:
        self._rawText = value if value is not None else ""
        self._applyElide()

    @property
    def Alignment(self) -> Qt.AlignmentFlag:
        return self.alignment()

    @Alignment.setter
    def Alignment(self, value: Qt.AlignmentFlag) -> None:
        self.setAlignment(value)

    @property
    def ElideMode(self) -> Qt.TextElideMode:
        return self._elideMode

    @ElideMode.setter
    def ElideMode(self, value: Qt.TextElideMode) -> None:
        if value == self._elideMode:
            return
        self._elideMode = value
        self._applyElide()

    # ================================================================================== private
    def _applyElide(self) -> None:
        if self._elideMode == Qt.TextElideMode.ElideNone:
            self.setText(self._rawText)
            return

        lMetrics = self.fontMetrics()
        lAvailable = self.width() if self.width() > 0 else 200
        lElided = lMetrics.elidedText(self._rawText, self._elideMode, lAvailable)
        self.setText(lElided)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._applyElide()
