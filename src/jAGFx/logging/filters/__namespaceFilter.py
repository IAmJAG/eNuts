# ==================================================================================
import logging

# ==================================================================================
from typing import Dict

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
        # Name-based allow list (THIRD_PARTY_LOGGERS via suppressedLogger)
        if record.name in self.LOG_NAMES.keys():
            logLevel = self.LOG_NAMES[record.name]
            if isinstance(logLevel, str):
                logLevel = logging._nameToLevel[logLevel]

            return record.levelno >= logLevel

        lLogLevel: int = self._defaultLogLevel
        try:
            lCaller: BaseSourceInformation = getattr(record, "caller", None)

            # Unowned / third-party records have no project-injected caller.
            # Formatter would later tag them NOT.MINE for display; drop them here
            # so they never reach the handler (filter runs before format).
            if lCaller is None:
                return False

            fqn = lCaller.fullyQualifiedName or ""
            # Explicit NOT.MINE tag (fallback / unowned)
            if fqn == "NOT.MINE" or fqn.startswith("NOT.MINE."):
                return False

            for ns, lvl in self.NAMESPACE_LEVELS.items():
                if fqn.startswith(ns):
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
        cls.LOG_NAMES.pop(name, None)
