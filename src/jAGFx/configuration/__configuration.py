# ==================================================================================
from __future__ import annotations

# ==================================================================================
from json import dumps, load
from typing import Dict, Optional

# ==================================================================================
from ..serializer import Serializable
from ..types.interface.configuration import iConfiguration


# ==================================================================================
class Configuration(Serializable, iConfiguration):
    def __init__(self): 
        super().__init__()
        self._sections: iConfiguration = dict[str, iConfiguration]()

    @property
    def sections(self) -> Dict[str, iConfiguration]:
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
        assert isinstance(sectionPath, str), "sectionPath must be a string."

        sections: list[str] = sectionPath.split(".")        
        current: Optional[iConfiguration] = None
        for section in sections:
            if section not in current.sections:
                return None

            current = current.sections[section]

        return current
    
    def addSection(self, sectionPath: str, newSection: Optional[iConfiguration]) -> iConfiguration: 
        assert isinstance(sectionPath, str), "sectionPath must be a string."

        sections: list[str] = sectionPath.split(".")        
        current: Optional[iConfiguration] = None
        for section in sections[:-1]:
            if section not in current.sections:
                current.sections[section] = Configuration()
            current = current.sections[section]

        current.sections[sections[-1]] = newSection
        
    
    def removeSection(self, sectionPath: str) -> iConfiguration: 
        assert isinstance(sectionPath, str), "sectionPath must be a string."

        sections: list[str] = sectionPath.split(".")        
        current: Optional[iConfiguration] = None
        for section in sections[:-1]:
            if section not in current.sections:
                current.sections[section] = Configuration()
            current = current.sections[section]

        del current.sections[sections[-1]]

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