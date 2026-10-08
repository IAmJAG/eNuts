# ==================================================================================================
from importlib import import_module
from logging import DEBUG, ERROR, INFO, WARNING, getLogger
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
    # asyncio/proactor emits high-volume DEBUG ("Got events from poll", "Invoking event callback")
    # under Windows IOCP; keep app VERBOSE but mute the stdlib asyncio logger.
    getLogger("asyncio").setLevel(WARNING)
    lArgs, lKWArgs = ProcessArguments(args)
    return _program(*lArgs, **lKWArgs)

# ==================================================================================================
if __name__ == "__main__":
    result = program(argv)
    exit(result)
