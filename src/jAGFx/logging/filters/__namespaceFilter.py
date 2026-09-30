# ==================================================================================
import logging

# ==================================================================================
from jAGFx.singleton import SingletonC

# ==================================================================================
from ..data import BaseSourceInformation


# ==================================================================================
@SingletonC
class NamespaceFilter(logging.Filter):
    NAMESPACE_LEVELS = {}
    def __init__(self, defaultLogLevel: int = logging.NOTSET) -> None:
        super().__init__()
        self._defaultLogLevel: int = defaultLogLevel

    def filter(self, record: logging.LogRecord) -> bool:
        lLogLevel: int = self._defaultLogLevel        
        try:
            if record:                
                lCaller: BaseSourceInformation = getattr(record, "caller", None)
                if lCaller:
                    ns: str
                    for ns, lvl in self.NAMESPACE_LEVELS.items():
                        if lCaller.FullyQualifiedName.startswith(ns):
                            lLogLevel = lvl
                            break

            return record.levelno >= lLogLevel

        except Exception as ex:
            raise ex

    @classmethod
    def setNSLogLevel(cls, ns: str, lvl: int = logging.NOTSET):
        cls.NAMESPACE_LEVELS[ns] = lvl
