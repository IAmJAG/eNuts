# ==================================================================================
from asyncio import Event as asyncEvent

# ==================================================================================
from PySide6.QtGui import QIcon

# ==================================================================================
from jAGFx.types.interface.configuration import iApplicationConfiguration
from jAGQt.window.windowBase import WindowBase

# ==================================================================================
from ..types.interface.application import iApplicationInformation


# ==================================================================================
class ApplicationInformation(WindowBase, iApplicationInformation):
    def __init__(
        self: WindowBase, shutdownEvent: asyncEvent, cfg: iApplicationConfiguration, *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self._config = cfg        
        self._applicationId = cfg.applicationId
        self._company = cfg.company
        self._logo = cfg.logo
        self._shutdownEvent = shutdownEvent

    def closeEvent(self, event):
        self._shutdownEvent.set()
        return super().closeEvent(event)

    @property
    def config(self: WindowBase) -> iApplicationConfiguration:
        return self._config

    @config.setter
    def config(self: WindowBase, value: iApplicationConfiguration):
        self._config = value
    
    @property
    def title(self: WindowBase):
        return self.windowTitle()

    @title.setter
    def title(self: WindowBase, value: str):
        self.setWindowTitle(value)

    @property
    def company(self: WindowBase) -> str:
        return self.config.company

    @company.setter
    def company(self: WindowBase, value: str):
        self._company = value

    @property
    def applicationId(self: WindowBase) -> str:
        return self._applicationId

    @applicationId.setter
    def applicationId(self: WindowBase, value: str):
        self._applicationId = value

    @property
    def logo(self: WindowBase) -> str:
        return self._logo

    @logo.setter
    def logo(self: WindowBase, value: str) -> None:
        self._logo = value

    @property
    def icon(self: WindowBase) -> QIcon:
        return self.windowIcon()

    @icon.setter
    def icon(self: WindowBase, value: QIcon):
        self.setWindowIcon(value)

    @property
    def FQN(self: WindowBase) -> str:
        return f"[{self.applicationId}]"

    @property
    def name(self: WindowBase) -> str:
        return self.objectName()

    @name.setter
    def name(self: WindowBase, value: str):
        self.setObjectName(value)

    @property
    def Parent(self) -> WindowBase:
        return None