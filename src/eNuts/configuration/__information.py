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
    def _wInitializeInfo(self: iMainWindowBase):
        cfg: iConfiguration | iApplicationConfiguration | iENUTSConfiguration = eNutsConfiguration()

        self.Title = cfg.title
        self.Icon = QIcon(os.path.join(getICONPath(), f"{cfg.icon}.png"))
        self._company: str = cfg.company
        self._appId: str = cfg.applicationId
        self._logo: str = cfg.icon
        self._config: iConfiguration | iApplicationConfiguration | iENUTSConfiguration = cfg

    # region [PROPERTIES]
    @property
    def Config(self) -> iConfiguration | iApplicationConfiguration | iENUTSConfiguration:
        return self._config

    @property
    def Title(self: QWidget):
        return self.windowTitle()

    @Title.setter
    def Title(self: QWidget, value: str):
        self.setWindowTitle(value)

    @property
    def Icon(self: QWidget) -> QIcon:
        return self.windowIcon()

    @Icon.setter
    def Icon(self: QWidget, value: QIcon):
        self.setWindowIcon(value)

    @property
    def Company(self) -> str:
        return self._company

    @Company.setter
    def Company(self, value: str):
        self._company = value

    @property
    def ApplicationId(self) -> str:
        return self._appId

    @ApplicationId.setter
    def ApplicationId(self, value: str):
        self._appId = value

    @property
    def Logo(self) -> str:
        return self._logo

    @Logo.setter
    def Logo(self, value: str) -> None:
        self._logo = value

    @property
    def FQN(self) -> str:
        return f"[{self.ApplicationId}]"

    @property
    def Name(self: QWidget) -> str:
        return self.objectName()

    @Name.setter
    def Name(self: QWidget, value: str):
        self.setObjectName(value)

    @property
    def Parent(self) -> QWidget:
        return None
    # endregion