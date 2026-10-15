# ==================================================================================
import os

# ==================================================================================
from threading import RLock

# ==================================================================================
from ..types.interface.configuration import iApplicationConfiguration
from .__configuration import Configuration, iConfiguration

# ==================================================================================
CONFIG_PATH: str = "config"
CONFIG_FILENAME: str = "appconfig.json"
# ==================================================================================

# ==================================================================================
class ApplicationConfiguration(Configuration, iApplicationConfiguration):
    def __init__(
        self, title: str = "", company: str = "",
        applicationId: str = "", logo: str = ""
    ) -> None:
        super().__init__()
        
        self._title: str = title        
        self._company: str = company
        self._applicationId: str = applicationId
        self._logo: str = logo

        self.Properties.extend(["title", "company", "applicationId", "logo"])

        self._lock: RLock = RLock()
        self._updatedAttributes: set = set()
        self._savePath: str = ""
   
    @property
    def updatedAttributes(self) -> set:
        with self._lock:
            return self._updatedAttributes

    @property
    def isDirty(self) -> bool:
        with self._lock:
            return len(self._updatedAttributes) > 0
    
    @property
    def title(self) -> str:        
        with self._lock: 
            return self._title

    @property
    def company(self) -> str:
        with self._lock: 
            return self._company

    @property
    def applicationId(self) -> str:
        with self._lock: 
            return self._applicationId

    @property
    def logo(self) -> str:
        with self._lock:
            return self._logo

    def load(self, path: str = None) -> iConfiguration:
        savePath: str = (
            path or self._savePath or os.path.join(CONFIG_PATH, CONFIG_FILENAME)
        )
        with self._lock:
            super().load(savePath)            
        self._updatedAttributes.clear()

    def save(self, path: str = None) -> None:        
        if self.isDirty:
            savePath: str = (
                path or self._savePath or os.path.join(CONFIG_PATH, CONFIG_FILENAME)
            )

            with self._lock:
                os.makedirs(os.path.dirname(savePath), exist_ok=True)
                super().save(savePath)
            self._updatedAttributes.clear()
