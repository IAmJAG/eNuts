# ==================================================================================================
from importlib import import_module
from logging import WARNING, getLogger
from sys import argv

# ==================================================================================================
import __monkeyPatch

# ==================================================================================================
from jAGFx.logging import VERBOSE
from utilities import launchModule

# ==================================================================================================
LOG_LEVEL: int = VERBOSE
# ==================================================================================================


# ==================================================================================================
def _silenceAsyncioLogs() -> None:
    """Mute high-volume Windows IOCP / proactor DEBUG lines."""
    for lName in ("asyncio", "asyncio.proactor", "asyncio.windows_events"):
        lLogger = getLogger(lName)
        lLogger.setLevel(WARNING)
        lLogger.propagate = False


# ==================================================================================================
def _program(module: str, app: str, clean: bool = False, *args, **kwargs):
    try:
        moduleNS: str = f"{module}.{app}"
        addFileHandler(moduleNS, LOG_LEVEL)
        debug(f"Current module namespace: {moduleNS}")

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


# ==================================================================================================
def program(args: list = argv):
    setupLogging("", LOG_LEVEL)
    _silenceAsyncioLogs()
    lArgs, lKWArgs = ProcessArguments(args)
    return _program(*lArgs, **lKWArgs)


# ==================================================================================================
if __name__ == "__main__":
    result = program(argv)
    exit(result)
