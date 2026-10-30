# ==================================================================================
import logging

# ==================================================================================
from typing import Dict, List

# ==================================================================================
from jAGFx.singleton import SingletonC

# ==================================================================================
from ..data import BaseSourceInformation


# ==================================================================================
@SingletonC
class NamespaceFilter(logging.Filter):
    NAMESPACE_LEVELS = {}
    LOG_NAMES: Dict[str, int] = dict[str, int]()

    def __init__(self, defaultLogLevel: int = logging.NOTSET) -> None:
        super().__init__()
        self._defaultLogLevel: int = defaultLogLevel

    def filter(self, record: logging.LogRecord) -> bool:
        if record.name in self.LOG_NAMES.keys():
            logLevel = self.LOG_NAMES[record.name]
            if isinstance(logLevel, str):
                logLevel = logging._nameToLevel[logLevel]

            return record.levelno >= logLevel

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

    @classmethod
    def addNameFilter(cls, name: str, lvl: int = logging.NOTSET):
        cls.LOG_NAMES.update({name: lvl})

    @classmethod
    def removeNameFilter(cls, name: str, lvl: int = logging.NOTSET):
        cls.LOG_NAMES.remove(name)
