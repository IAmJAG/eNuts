# ==================================================================================
from __future__ import annotations

# ==================================================================================
from json import dumps, load

# ==================================================================================
from ..serializer import Serializable
from ..types.interface.configuration import iConfiguration


# ==================================================================================
class Configuration(Serializable, iConfiguration):
    def __init__(self): 
        super().__init__()
        self._sections: iConfiguration = {}

    @property
    def sections(self) -> dict[str, iConfiguration]:
        return self._sections

    def load(self, path: str = None) -> iConfiguration:            
        savePath = path if path else getattr(self, "_savePath", None)        
        if savePath is None: 
            raise Exception("No save path specified")
                
        with open(path) as file: cfgObj: str = load(fp=file)
        self.decode(cfgObj)

    def save(self, path: str = None) -> None:
        savePath = path if path else getattr(self, "_savePath", None)
        if savePath is None: 
            raise Exception("No save path specified")

        with open(savePath, "w") as file:
            cfgStr: str = dumps(self.encode())
            file.write(cfgStr)

    def getSection(self, sectionPath: str) -> iConfiguration:
        if not isinstance(sectionPath, str):
            raise TypeError("sectionPath must be a string.")

        sections: list[str] = sectionPath.split(".")

        if not sections or any(not section for section in sections):
            raise ValueError("sectionPath must contain valid section names.")

        current: Configuration = self

        for section in sections:
            if section not in current._sections:
                current._sections[section] = Configuration()

            current = current._sections[section]

        return current

    # region [PICKLE READINESS]
    def __getstate__(self):
        lDicState = super().__getstate__()
        lInstanceState = {}
        return (lDicState, lInstanceState)

    def __setstate__(self, state):
        lDicState, lInstanceState = state
        self.__setstate__(lDicState)
        self.__dict__.update(lInstanceState)
    # endregion