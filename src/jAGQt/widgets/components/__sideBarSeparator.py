# ==================================================================================
# src/jAGQt/widgets/components/__sideBarSeparator.py
# ==================================================================================
from enum import Enum, auto
from typing import Optional

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QSizePolicy, QWidget

# ==================================================================================
from jAGQt.types.components import ComponentBase


# ==================================================================================
class SeparatorType(Enum):
    Line = auto()
    Stretcher = auto()


# ==================================================================================
class SideBarSeparator(QFrame, ComponentBase):
    """Independent separator or stretcher that can be inserted between SideBar items."""

    def __init__(
        self,
        separatorType: SeparatorType = SeparatorType.Line,
        thickness: int = 1,
        parent: Optional[QWidget] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)

        self.setObjectName("SideBarSeparator")
        self._separatorType: SeparatorType = separatorType
        self._thickness: int = max(0, thickness)

        self._applyType()

    # ================================================================================== public API
    def SetType(self, separatorType: SeparatorType) -> None:
        self.Type = separatorType

    # ================================================================================== properties
    @property
    def Type(self) -> SeparatorType:
        return self._separatorType

    @Type.setter
    def Type(self, value: SeparatorType) -> None:
        if value == self._separatorType:
            return
        self._separatorType = value
        self._applyType()

    @property
    def Thickness(self) -> int:
        return self._thickness

    @Thickness.setter
    def Thickness(self, value: int) -> None:
        lValue = max(0, int(value))
        if lValue == self._thickness:
            return
        self._thickness = lValue
        self._applyType()

    # ================================================================================== private
    def _applyType(self) -> None:
        if self._separatorType == SeparatorType.Stretcher:
            self.setFrameShape(QFrame.Shape.NoFrame)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.setFixedHeight(0)
            self.setMinimumHeight(0)
            self.setMaximumHeight(16777215)
        else:
            self.setFrameShape(QFrame.Shape.HLine)
            self.setFrameShadow(QFrame.Shadow.Sunken)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            self.setFixedHeight(self._thickness)
