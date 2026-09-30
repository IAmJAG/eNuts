# ==================================================================================
# src/jAGFx/configuration/__applicationConfig.py
# ==================================================================================
import os

# ==================================================================================
from json import dumps, load
from threading import RLock
from typing import TypeVar

# ==================================================================================
from ..types.interface.serializer import iSerializable
from .__configuration import Configuration, iConfiguration

# ==================================================================================
ConfigType = TypeVar("T", bound=iConfiguration)
CFGINSTANCE: iConfiguration = None
# ==================================================================================
__all__ = ["ApplicationConfiguration", "CFGINSTANCE"]
# ==================================================================================
LOGGER_SECTION = "LOGGER"
CONFIG_PATH: str = "config"
CONFIG_FILENAME: str = "appconfig.json"
# ==================================================================================

# ==================================================================================
class ApplicationConfiguration(Configuration, iSerializable):
    def __init__(self, Title: str = "", Company: str = "", ApplicationId: str = "", Icon: str = "") -> None:
        super().__init__()

        self._updatedAttributes: set = set()
        self._savePath: str = ""
        self._title: str = Title        
        self._company: str = Company
        self._applicationId: str = ApplicationId
        self._icon: str = Icon
        self._style: str = "dark"
        self._lock: RLock = RLock()
        self.Properties.extend(["title", "company", "applicationId", "icon", "style"])

    @property
    def sections(self) -> dict[str, iConfiguration]:
        with self._lock:
            return super().sections
    
    @property
    def updatedAttributes(self) -> set:
        with self._lock:
            return self._updatedAttributes

    @property
    def isDirty(self) -> bool:
        with self._lock:
            return len(self._updatedAttributes) > 0

    @property
    def style(self) -> str:
        with self._lock:
            return self._style

    @style.setter
    def style(self, value: str) -> None:
        with self._lock:
            self._style = value

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
    def icon(self) -> str:
        with self._lock:
            return self._icon

    def load(self, path: str = None) -> iConfiguration:
        self._savePath = (path or self._savePath or os.path.join(CONFIG_PATH, CONFIG_FILENAME))

        with open(self._savePath) as file:
            cfgStr: str = load(fp=file)

        with self._lock:
            self.decode(cfgStr)
            self._updatedAttributes.clear()

    def save(self, path: str = None) -> None:        
        if self.isDirty:
            savePath: str = (
                path or self._savePath or os.path.join(CONFIG_PATH, CONFIG_FILENAME)
            )
            with self._lock:
                os.makedirs(os.path.dirname(savePath), exist_ok=True)
                with open(savePath, "w") as file:
                    cfgStr: str = dumps(self.encode())
                    file.write(cfgStr)
                    self._updatedAttributes.clear()
