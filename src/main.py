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
        lModule: launchModule = import_module(f"{module}.{app}")
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
    addFileHandler("eNuts", LOG_LEVEL)    
    debug(f"Current module namespace: {__name__}")
    lArgs, lKWArgs = ProcessArguments(args)
    return _program(*lArgs, **lKWArgs)

# ==================================================================================================
if __name__ == "__main__":
    result = program(argv)
    exit(result)
