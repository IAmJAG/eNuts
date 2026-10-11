# ==================================================================================
# src/jAGQt/widgets/SideBar/components/__sideBarText.py
# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QSizePolicy, QWidget

# ==================================================================================
from jAGFx.workflow import workflow

# ==================================================================================
from ...components import ComponentBase

# ==================================================================================
QPolicy = QSizePolicy.Policy
# ==================================================================================

# ==================================================================================
@workflow
class SideBarTitle(QLabel, ComponentBase):
    OBJECT_NAME = "W_SIDEBAR_TITLE"
    def __init__(
        self, text: str = "",
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
        elideMode: Qt.TextElideMode = Qt.TextElideMode.ElideRight, *args, **kwargs,
    ) -> None:
        OBJNAME: str = kwargs.pop("objectName", self.OBJECT_NAME)   
        super().__init__(objectName=OBJNAME, *args, **kwargs)

        self._alignment: Qt.AlignmentFlag = alignment
        self._elideMode: Qt.TextElideMode = elideMode
        self._text: str = text

    def _wInitializeUI(self):
        text: str = self._text
        elideMode: Qt.TextElideMode = self._elideMode
        alignment: Qt.AlignmentFlag = self._alignment

        del self._alignment

        self._elideMode: Qt.TextElideMode = elideMode
        self.setSizePolicy(QPolicy.Expanding, QPolicy.Preferred)
        self.setWordWrap(False)
        self.setAlignment(alignment)      

        self._applyElide()
    
    # ==================================================================================
    @property
    def Text(self) -> str:
        return self._text

    @Text.setter
    def Text(self, value: str) -> None:        
        self._text = value
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
        if value == self._elideMode: return
        self._elideMode = value
        self._applyElide()

    # ==================================================================================
    def _applyElide(self) -> None:
        text: Optional[str] = self.text()
        if text == self.text(): return

        if self._elideMode == Qt.TextElideMode.ElideNone:
            self.setText(text)
            return

        elideMode: Qt.TextElideMode = self._elideMode        
        width: int = self.width()        
        metrics = self.fontMetrics()
        available = width if width > 0 else 200

        elided = metrics.elidedText(text, elideMode, available)
        self.setText(elided)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._applyElide()
