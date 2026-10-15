# ==================================================================================
import os

# ==================================================================================
from jAGFx.configuration import ApplicationConfiguration
from jAGFx.singleton import SingletonC

# ==================================================================================
from ..types.interface.configuration import iENUTSConfiguration

# ==================================================================================
CONFIG_PATH: str = os.path.join(".", "config", "eNuts")
# ==================================================================================

@SingletonC
class eNutsConfiguration(ApplicationConfiguration, iENUTSConfiguration):
    def __init__(self):
        ApplicationConfiguration.__init__(self)
        self._savePath = os.path.join(CONFIG_PATH, "appconfig.json")
        self._theme: str = "dracula"
        self._assetFolder: str ="assets"        
        self.Properties.extend(["theme", "assetFolder"])
        self.load()

    @property
    def theme(self):
        return self._theme

    @property
    def assetFolder(self):
        return self._assetFoder
    
    def save(self, path=None) -> iENUTSConfiguration:
        super().save(path)
        return self
    
    def load(self, path=None) -> iENUTSConfiguration:
        super().load(path)
        return self