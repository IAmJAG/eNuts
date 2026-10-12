# ==================================================================================
# src/jAGQt/widgets/SideBar/components/__sideBarSeparator.py
# ==================================================================================
from enum import Enum, auto

# ==================================================================================
from PySide6.QtWidgets import QFrame, QSizePolicy, QWidget

# ==================================================================================
from jAGFx.workflow import workflow

# ==================================================================================
from ...components import ComponentBase
from ..types import SideBarItemSeparatorType

# ==================================================================================
QPolicy = QSizePolicy.Policy
# ==================================================================================


# ==================================================================================
@workflow
class Separator(QFrame, ComponentBase):
    OBJECT_NAME = "W_SIDEBAR_SEPARATOR"

    def __init__(
        self,
        separatorType: SideBarItemSeparatorType = SideBarItemSeparatorType.Line,
        thickness: int = 1,
        *args,
        **kwargs,
    ) -> None:
        OBJNAME: str = kwargs.pop("objectName", self.OBJECT_NAME)
        super().__init__(objectName=OBJNAME, *args, **kwargs)
        self._separatorType: SideBarItemSeparatorType = separatorType
        self._thickness: int = max(0, int(thickness))

    def _wInitializeUI(self) -> None:
        self._applyType()

    # ==================================================================================
    def setType(self, separatorType: SideBarItemSeparatorType) -> None:
        self.Type = separatorType

    # ==================================================================================
    @property
    def type(self) -> SideBarItemSeparatorType:
        return self._separatorType

    @type.setter
    def type(self, value: SideBarItemSeparatorType) -> None:
        if value == self._separatorType:
            return
        self._separatorType = value
        self._applyType()

    @property
    def thickness(self) -> int:
        return self._thickness

    @thickness.setter
    def thickness(self, value: int) -> None:
        lValue: int = max(0, int(value))
        if lValue == self._thickness:
            return
        self._thickness = lValue
        self._applyType()

    # ==================================================================================
    def _applyType(self) -> None:
        if self._separatorType is SideBarItemSeparatorType.Stretcher:
            self.setFrameShape(QFrame.Shape.NoFrame)
            self.setSizePolicy(QPolicy.Expanding, QPolicy.Expanding)
            self.setMinimumHeight(0)
            self.setMaximumHeight(16777215)
        else:
            thickness: int = max(1, self._thickness)
            self.setFrameShape(QFrame.Shape.HLine)
            self.setFrameShadow(QFrame.Shadow.Sunken)
            self.setSizePolicy(QPolicy.Expanding, QPolicy.Fixed)
            self.setFixedHeight(thickness)

        self.setProperty(
            "separatorType",
            "stretcher" if self._separatorType is SideBarItemSeparatorType.Stretcher else "line",
        )
        self.style().unpolish(self)
        self.style().polish(self)
