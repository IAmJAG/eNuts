# ==================================================================================
from json import dumps, load

# ==================================================================================
from ..serializer import Serializable
from ..types.interface.configuration import iConfiguration

# ==================================================================================
__all__ = ["Configuration"]
# ==================================================================================

# ==================================================================================
class Configuration(Serializable, iConfiguration):
    def __init__(self):
        super().__init__()
        self._sections: dict[str, iConfiguration] = {}
        self._updatedAttributes: set = set()
        self.Properties.extend(["sections"])
    
    @property
    def sections(self) -> dict[str, iConfiguration]:
        return self._sections

    @property
    def updatedAttributes(self) -> set:
        return self._updatedAttributes

    @property
    def isDirty(self) -> bool:
        return len(self._updatedAttributes) > 0

    def __setattr__(self, name: str, value):
        if hasattr(self, "_properties") and name in [f"_{p}" for p in self.Properties]:
            if value != getattr(self, name, None):
                self._updatedAttributes.add(name)
            return super().__setattr__(name, value)
                    
        return super().__setattr__(name, value)

    def load(self, path: str) -> iConfiguration:
        self._savePath = path
        with open(path) as file: cfgObj: str = load(fp=file)
        self.decode(cfgObj)
        self._updatedAttributes.clear()

    def save(self, path: str = None) -> None:
        savePath: str = path or self._savePath
        with open(savePath, "w") as file:
            cfgStr: str = dumps(self.encode())
            file.write(cfgStr)
            self._updatedAttributes.clear()

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