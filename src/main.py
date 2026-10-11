# ==================================================================================================
from importlib import import_module
from logging import (
    CRITICAL,
    NOTSET,
    WARNING,
    Filter,
    LogRecord,
    getLogger,
    root,
)
from os import environ
from sys import argv
from typing import List

# ==================================================================================================
import __monkeyPatch

# ==================================================================================================
from jAGFx.logging import VERBOSE, suppressedLogger
from utilities import launchModule

# ==================================================================================================
LOG_LEVEL: int = VERBOSE
THIRD_PARTY_LOG_LEVEL: int = WARNING
THIRD_PARTY_LOGGERS: List[str] = [
    "asyncio",
    "qasync._windows._EventPoller",
    "qasync._windows._EventWorker",
    "qasync._windows._IocpProactor",
    "qasync.QThreadExecutor",
    "qasync._QThreadWorker",
]
# ==================================================================================================

# ==================================================================================================
def _program(module: str, app: str, clean: bool = False, *args, **kwargs):
    try:
        moduleNS: str = f"{module}.{app}"
        addFileHandler(moduleNS, LOG_LEVEL)

        verbose(f">>{moduleNS}")
        lModule: launchModule = import_module(moduleNS)
        lArguments: list[str] = RebuildArguments(argv[0], *args, **kwargs)
        lExitCode = lModule.program(lArguments)
        return lExitCode

    except Exception as ex:
        raise ex

    finally:
        if clean:
            lFolders, lFiles = PyCacheClean()
            debug(f"Deleted {lFolders} folders and {lFiles} files")

        verbose(f"<<{moduleNS}")


# ==================================================================================================
def program(args: list = argv):
    setupLogging("", LOG_LEVEL)
    suppressedLogger(THIRD_PARTY_LOGGERS, THIRD_PARTY_LOG_LEVEL)
    lArgs, lKWArgs = ProcessArguments(args)
    return _program(*lArgs, **lKWArgs)

# ==================================================================================================
if __name__ == "__main__":
    result = program(argv)
    exit(result)
