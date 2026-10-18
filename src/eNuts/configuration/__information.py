# ==================================================================================
# src/eNuts/types/interface/UI/mwMixin/__applicationInfo.py
# ==================================================================================
import os

# ==================================================================================
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget

# ==================================================================================
from jAGFx.types.interface.configuration import (
    iApplicationConfiguration,
    iConfiguration,
)
from jAGQt.types.interface.window import iMainWindowBase
from utilities.io import getICONPath

# ==================================================================================
from ..configuration import eNutsConfiguration
from ..types.interface.configuration import iENUTSConfiguration


# ==================================================================================
class ApplicationInformation:
    # region [PROPERTIES]
    @property
    def title(self: QWidget):
        return self.windowTitle()

    @title.setter
    def title(self: QWidget, value: str):
        self.setWindowTitle(value)

    @property
    def icon(self: QWidget) -> QIcon:
        return self.windowIcon()

    @icon.setter
    def icon(self: QWidget, value: QIcon):
        self.setWindowIcon(value)

    @property
    def company(self) -> str:
        return self._company

    @company.setter
    def company(self, value: str):
        self._company = value

    @property
    def applicationId(self) -> str:
        return self._applicationID

    @applicationId.setter
    def applicationId(self, value: str):
        self._applicationID = value

    @property
    def logo(self) -> str:
        return self._logo

    @logo.setter
    def logo(self, value: str) -> None:
        self._logo = value

    @property
    def FQN(self) -> str:
        return f"[{self.applicationId}]"

    @property
    def name(self: QWidget) -> str:
        return self.objectName()

    @name.setter
    def name(self: QWidget, value: str):
        self.setObjectName(value)

    @property
    def Parent(self) -> QWidget:
        return None
    # endregion