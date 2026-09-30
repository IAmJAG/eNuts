# ==================================================================================================
import builtins

# ==================================================================================================
from asyncio import sleep as asyncSleep
from time import sleep

# ==================================================================================================
from jAGFx.logging import (
    addFileHandler,
    critical,
    debug,
    error,
    fatal,
    info,
    removeFileHandler,
    setNamespaceLevel,
    setupLogging,
    verbose,
    warning,
)

# ==================================================================================================
from jAGFx.types import Is, isAny, isListOfT, isNone, isUnion
from utilities import ProcessArguments, PyCacheClean, RebuildArguments, StripAnsi

# ==================================================================================================
# GLOBAL default value
# ==================================================================================================
setattr(builtins, "EMPTY", "")
setattr(builtins, "EMPTYLIST", [])
setattr(builtins, "EMPTYDICT", {})
setattr(builtins, "EMPTYSET", set())
setattr(builtins, "TAB", "\t")
setattr(builtins, "LF", "\n")

# ==================================================================================================
# GLOBAL functions - directory/cache management
# ==================================================================================================
setattr(builtins, "PyCacheClean", PyCacheClean)

# ==================================================================================================
# GLOBAL functions - argument management
# ==================================================================================================
setattr(builtins, "ProcessArguments", ProcessArguments)
setattr(builtins, "RebuildArguments", RebuildArguments)

# ==================================================================================================
# GLOBAL functions - time extensions
# ==================================================================================================
setattr(builtins, "wait", sleep)
setattr(builtins, "asyncWait", asyncSleep)

# ==================================================================================================
# GLOBAL functions - type check
# ==================================================================================================
setattr(builtins, "isUnion", isUnion)
setattr(builtins, "isAny", isAny)
setattr(builtins, "isNone", isNone)
setattr(builtins, "isListOfT", isListOfT)
setattr(builtins, "Is", Is)

# ==================================================================================================
# GLOBAL functions - logging
# ==================================================================================================
setattr(builtins, "setNamespaceLevel", setNamespaceLevel)
setattr(builtins, "setupLogging", setupLogging)
setattr(builtins, "addFileHandler", addFileHandler)
setattr(builtins, "removeFileHandler", removeFileHandler)

setattr(builtins, "verbose", verbose)
setattr(builtins, "debug", debug)
setattr(builtins, "error", error)
setattr(builtins, "info", info)
setattr(builtins, "warning", warning)
setattr(builtins, "critical", critical)
setattr(builtins, "fatal", fatal)

# ==================================================================================================
# GLOBAL functions - string
# ==================================================================================================
setattr(builtins, "StripAnsi", StripAnsi)

