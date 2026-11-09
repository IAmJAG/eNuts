# ==================================================================================
from __future__ import annotations

# ==================================================================================
from json import dumps, load
from typing import Dict, Optional

# ==================================================================================
from ..serializer import Serializable
from ..types.interface.configuration import iConfiguration


class Configuration(Serializable, iConfiguration):
    def __init__(self):
        super().__init__()
        self._sections: Dict[str, iConfiguration] = {}

    @property
    def sections(self) -> Dict[str, iConfiguration]:
        return self._sections

    


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

    @staticmethod
    def _parseSectionPath(sectionPath: str) -> list[str]:
        if not isinstance(sectionPath, str):
            raise TypeError("sectionPath must be a string.")

        sections = sectionPath.split(".")

        if any(not section for section in sections):
            raise ValueError("sectionPath must contain valid section names.")

        return sections

    def getSection(self, sectionPath: str) -> Optional[iConfiguration]:
        sections = self._parseSectionPath(sectionPath)
        current: iConfiguration = self

        for section in sections:
            if section not in current.sections:
                return None

            current = current.sections[section]

        return current

    def exist(self, sectionPath: str) -> bool:
        return self.getSection(sectionPath) is not None

    def addSection(
        self, sectionPath: str, newSection: Optional[iConfiguration]
    ) -> iConfiguration:
        sections = self._parseSectionPath(sectionPath)
        current: iConfiguration = self

        for section in sections[:-1]:
            if section not in current.sections:
                current.sections[section] = Configuration()

            current = current.sections[section]

        if newSection is None:
            newSection = Configuration()

        current.sections[sections[-1]] = newSection

        return newSection

    def removeSection(self, sectionPath: str) -> iConfiguration:
        sections = self._parseSectionPath(sectionPath)
        current: iConfiguration = self

        for section in sections[:-1]:
            if section not in current.sections:
                raise KeyError(f"Configuration section not found: {sectionPath}")

            current = current.sections[section]

        section = sections[-1]

        if section not in current.sections:
            raise KeyError(f"Configuration section not found: {sectionPath}")

        return current.sections.pop(section)

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