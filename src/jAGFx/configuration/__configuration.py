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
        sectionPath: list[str] = sectionPath.split(".")

        # ResolveSection        
        toTarget: str = EMPTY
        for section in sectionPath:
            toTarget += f".{section}" if toTarget == EMPTY else section
            if section not in self._sections:
                self._sections[section] = Configuration()

            if toTarget == sectionPath:
                return self._sections[section]

        return None

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