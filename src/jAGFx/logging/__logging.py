# ==================================================================================
from logging import (
    CRITICAL,
    DEBUG,
    ERROR,
    FATAL,
    INFO,
    WARNING,
    addLevelName,
)
from sys import exc_info
from sys import exit as _exit

# ==================================================================================
from .__log import log

# ==================================================================================
VERBOSE: int = 5
addLevelName(VERBOSE, "VERBOSE")

EXITONERROR: bool = True
# ==================================================================================

# ==================================================================================
def _resolveErr(err: Exception | None) -> Exception | None:
    """Use explicit err, else the active exception from an enclosing except block."""
    if err is not None:
        return err
    lActive = exc_info()[1]
    if isinstance(lActive, BaseException):
        return lActive
    return None

# ==================================================================================
def verbose(message: str | tuple | list | dict, err: Exception = None):
    log(messages=message, level=VERBOSE, err=err)

# ==================================================================================
def debug(message: str | tuple | list | dict, err: Exception = None):
    log(messages=message, level=DEBUG, err=err)

# ==================================================================================
def info(message: str | tuple | list | dict, err: Exception = None):
    log(messages=message, level=INFO, err=err)

# ==================================================================================
def warning(message: str | tuple | list | dict, err: Exception = None):
    log(messages=message, level=WARNING, err=err)

# ==================================================================================
def error(message: str | tuple | list | dict, err: Exception = None):
    # Always attach traceback for ERROR+ (explicit err or active exception).
    # EXITONERROR only when the caller explicitly passed err=.
    lErr = _resolveErr(err)
    log(messages=message, level=ERROR, err=lErr)
    if err is not None:
        _exitOnError(err)

# ==================================================================================
def critical(message: str | tuple | list | dict, err: Exception = None):
    lErr = _resolveErr(err)
    log(messages=message, level=CRITICAL, err=lErr)
    if err is not None:
        _exitOnError(err)

# ==================================================================================
def fatal(message: str | tuple | list | dict, err: Exception = None):
    lErr = _resolveErr(err)
    log(messages=message, level=FATAL, err=lErr)
    if err is not None:
        _exitOnError(err)

# ==================================================================================
def _exitOnError(err: Exception):
    if EXITONERROR:
        lExitCode: int = -1
        if hasattr(err, "errno"):
            lExitCode = err.errno

        _exit(lExitCode)
