# ==================================================================================================
from importlib import import_module
from logging import CRITICAL, Filter, LogRecord, WARNING, getLogger, root
from os import environ
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
class _AsyncioProactorNoiseFilter(Filter):
    """Drop Windows IOCP proactor chatter regardless of logger level."""

    _C_NOISE = (
        "Got events from poll",
        "Invoking event callback",
        "Using proactor",
        "is running after closing",
    )

    def filter(self, record: LogRecord) -> bool:
        if record.name.startswith("asyncio"):
            return record.levelno >= WARNING
        try:
            lMsg = record.getMessage()
        except Exception:
            return True
        for lNoise in self._C_NOISE:
            if lNoise in lMsg:
                return False
        return True


# ==================================================================================================
def _silenceAsyncioLogs() -> None:
    """Mute high-volume Windows IOCP / proactor DEBUG lines."""
    # Prevent asyncio from enabling its own debug instrumentation.
    environ["PYTHONASYNCIODEBUG"] = "0"

    lFilter = _AsyncioProactorNoiseFilter()

    for lName in ("asyncio", "asyncio.proactor", "asyncio.windows_events"):
        lLogger = getLogger(lName)
        lLogger.setLevel(CRITICAL)
        lLogger.propagate = False
        lLogger.disabled = False
        # Strip existing handlers that may have been attached at DEBUG.
        for lHandler in list(lLogger.handlers):
            lLogger.removeHandler(lHandler)
        lLogger.addFilter(lFilter)

    # Also filter at root so any handler that still sees these records drops them.
    root.addFilter(lFilter)
    for lHandler in list(root.handlers):
        lHandler.addFilter(lFilter)
        if lHandler.level < WARNING:
            # Do not raise root handlers; only asyncio is silenced.
            pass


# ==================================================================================================
def _program(module: str, app: str, clean: bool = False, *args, **kwargs):
    try:
        moduleNS: str = f"{module}.{app}"
        addFileHandler(moduleNS, LOG_LEVEL)
        _silenceAsyncioLogs()  # re-apply after file handler registration
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
