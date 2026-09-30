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
from sys import exit as _exit

# ==================================================================================
from .__log import log

# ==================================================================================
VERBOSE: int = 5
addLevelName(VERBOSE, "VERBOSE")

EXITONERROR: bool = True
# ==================================================================================

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
    log(messages=message, level=ERROR, err=err)
    if err:
        _exitOnError(err)

# ==================================================================================
def critical(message: str | tuple | list | dict, err: Exception = None):
    log(messages=message, level=CRITICAL, err=err)
    if err:
        _exitOnError(err)

# ==================================================================================
def fatal(message: str | tuple | list | dict, err: Exception = None):
    log(messages=message, level=FATAL, err=err)
    if err:
        _exitOnError(err)

# ==================================================================================
def _exitOnError(err: Exception):
    if EXITONERROR:
        lExitCode: int = -1
        if hasattr(err, "errno"):
            lExitCode = err.errno

        _exit(lExitCode)