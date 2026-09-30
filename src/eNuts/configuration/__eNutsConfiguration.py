# ==================================================================================
import os

# ==================================================================================
from jAGFx.configuration import ApplicationConfiguration
from jAGFx.singleton import SingletonC
from jAGFx.types.interface.configuration import iConfiguration
from utilities.io import getStyleSheet

# ==================================================================================
from ..types.interface.configuration import iENUTSConfiguration

# ==================================================================================
CONFIG_PATH: str = os.path.join(".", "config", "eNuts")
# ==================================================================================

@SingletonC
class eNutsConfiguration(ApplicationConfiguration, iENUTSConfiguration, iConfiguration):
    def __init__(self):
        ApplicationConfiguration.__init__(self)
        self._savePath = os.path.join(CONFIG_PATH, "appconfig.json")
        self._assetFoder: str ="assets"
        self._LDPath: str = ""
        self._styleSheet = ""
        self.Properties.extend(["LDPath", "assetFolder"])
        self.load()

    @property
    def assetFolder(self):
        return self._assetFoder

    @property
    def LDPath(self):
        return self._LDPath

    @LDPath.setter
    def LDPath(self, value):
        self._LDPath = value

    @property
    def styleSheet(self):
        return self._styleSheet
    
    def save(self, path=None) -> iENUTSConfiguration:
        super().save(path)
        self._styleSheet = getStyleSheet(os.path.join(CONFIG_PATH, f"{self.style}.qss"))
        return self
    
    def load(self, path=None) -> iENUTSConfiguration:
        super().load(path)
        self._styleSheet = getStyleSheet(os.path.join(CONFIG_PATH, f"{self.style}.qss"))
        return self