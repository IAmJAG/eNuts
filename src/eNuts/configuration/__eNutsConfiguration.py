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
        self._theme: str = "dracula"
        self.Properties.extend(["assetFolder", "theme"])
        self.load()

    @property
    def assetFolder(self):
        return self._assetFoder

    @property
    def theme(self):
        return self._theme
    
    def save(self, path=None) -> iENUTSConfiguration:
        super().save(path)
        return self
    
    def load(self, path=None) -> iENUTSConfiguration:
        super().load(path)
        return self