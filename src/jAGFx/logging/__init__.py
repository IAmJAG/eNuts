# ==================================================================================
from .__logging import VERBOSE, critical, debug, error, fatal, info, verbose, warning
from .__utilities import (
    addFileHandler,
    removeFileHandler,
    setNamespaceLevel,
    setupLogging,
)

# ==================================================================================
__all__ = [
    "removeFileHandler",
    "setNamespaceLevel",
    "setupLogging",
    "addFileHandler",
    "VERBOSE"
    "verbose",
    "debug",
    "info",    
    "warning",
    "error",
    "critical",
    "fatal"
]
