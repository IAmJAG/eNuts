# ==================================================================================
import queue

# ==================================================================================
from logging import (
    INFO,
    Filter,
    Formatter,
    getLogger,
)
from logging.handlers import QueueHandler, QueueListener
from typing import Any, Dict, List

# ==================================================================================
import colorlog

# ==================================================================================
from .filters import NamespaceFilter
from .formatters import DefaultFormatter
from .handlers import DateRotatingFileHandler

# region
# ==================================================================================
DEF_FILE_HANDLER = {
    "filenameTemplate": "{name}{timestamp}",
    "dateFormat": "%Y%m%d",
    "maximumBackups": 10,
    "maximumLogs": 10,
    "directories": ["./LOGS/", "archive", "backup"],
    "maximumSize": 10000000,
    "logExtension": "log",
    "archiveTimeStampFormat": "%Y%m%d%H%M",
    "archiveRetention": 10,
}

DEF_FILE_FORMATTER: Dict[str, Any] = {
    "class": DefaultFormatter,
    "kwargs": {
        "style": "{",
        "fmt": "[{asctime}][{levelname:<8}][{caller}] {message}",
        "datefmt": "%Y%m%d",
    },
},


# ==================================================================================
fmtList = [
    "%(light_black)s[%(asctime)s]%(reset)s",
    "%(log_color)s[%(levelname)-8s]%(reset)s ",
    "%(log_color)s[%(caller)-8s]%(reset)s ",
    "%(message_log_color)s%(message)s%(reset)s",
]
C_LOG_FORMAT = "".join(fmtList)
C_LOG_COLORS = {
    "DEBUG": "light_black",
    "INFO": "cyan",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "purple",
    "VERBOSE": "light_green",
}
C_SECONDARY_COLORS = {
    "message": {
        "DEBUG": "green",
        "INFO": "cyan",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "purple",
        "VERBOSE": "light_green",
    }
}

G_LOG_QUEUE: queue.Queue | None = None
G_LOG_LISTENER: QueueListener | None = None
G_ACTIVE_HANDLERS: List[colorlog.StreamHandler] = []
G_NAMESPACE_LEVELS: Dict[str, int] = {}
G_DEFAULT_LEVEL = 5
# ==================================================================================
# endregion

# ==================================================================================
EXITONERROR: bool = True
# ==================================================================================

# ==================================================================================
def _getConsoleLogger(name: str) -> colorlog.StreamHandler:
    global G_ACTIVE_HANDLERS

    for handler in G_ACTIVE_HANDLERS:
        if isinstance(handler, colorlog.StreamHandler):
            # there could only be one console handler
            return handler

    lConsoleHandler: colorlog.StreamHandler = colorlog.StreamHandler()
    lConsoleHandler.set_name(name)
    lFormatter: DefaultFormatter = DefaultFormatter()
    # lFormatter: colorlog.ColoredFormatter = colorlog.ColoredFormatter(
    #     fmt=C_LOG_FORMAT,
    #     datefmt="%Y%m%d %H%M%S",
    #     log_colors=C_LOG_COLORS,
    #     secondary_log_colors=C_SECONDARY_COLORS,
    # )
    filter: NamespaceFilter = NamespaceFilter()
    NamespaceFilter.setNSLogLevel("NOT.MINE", G_DEFAULT_LEVEL)
    lConsoleHandler.setFormatter(lFormatter)
    lConsoleHandler.addFilter(filter)
    lConsoleHandler.propagate = True
    return lConsoleHandler

# ==================================================================================
def _refreshQueueListener() -> None:
    global G_LOG_LISTENER, G_LOG_QUEUE, G_ACTIVE_HANDLERS

    if G_LOG_LISTENER is not None:
        G_LOG_LISTENER.stop()

    if G_LOG_QUEUE is not None and G_ACTIVE_HANDLERS:
        G_LOG_LISTENER = QueueListener(G_LOG_QUEUE, *G_ACTIVE_HANDLERS, respect_handler_level=True)
        G_LOG_LISTENER.start()

# ==================================================================================
def setupLogging(root: str, defaultLevel: int = G_DEFAULT_LEVEL) -> None:
    global G_LOG_QUEUE, G_DEFAULT_LEVEL, G_ACTIVE_HANDLERS
    G_DEFAULT_LEVEL = defaultLevel

    if G_LOG_QUEUE is None:
        G_LOG_QUEUE = queue.Queue(-1)

    lConsoleHandler = _getConsoleLogger(root)
    if lConsoleHandler not in G_ACTIVE_HANDLERS:
        G_ACTIVE_HANDLERS.append(lConsoleHandler)

    _refreshQueueListener()

    lQueueHandler = QueueHandler(G_LOG_QUEUE)
    lRootLogger = getLogger(root)
    lRootLogger.setLevel(G_DEFAULT_LEVEL)
    lRootLogger.addHandler(lQueueHandler)
    lRootLogger.propagate = True

# ==================================================================================
def addFileHandler(
    name: str, defaultLevel: int = G_DEFAULT_LEVEL, 
    formatter: Formatter = DEF_FILE_FORMATTER,
    filter: Filter = None
) -> None:
    global G_ACTIVE_HANDLERS, G_DEFAULT_LEVEL
    G_DEFAULT_LEVEL = defaultLevel

    if name in G_ACTIVE_HANDLERS: 
        warning(f"File handler {name} already exists")
        return

    lHandlerArgs: Dict = DEF_FILE_HANDLER.copy()
    lHandlerArgs["filenameTemplate"] = f"{name}.{{timestamp}}"
    
    lHandler: DateRotatingFileHandler = DateRotatingFileHandler(**lHandlerArgs)    
    lHandler.setLevel(defaultLevel)
    
    if formatter == DEF_FILE_FORMATTER:        
        formatter = DEF_FILE_FORMATTER[0]["class"](**DEF_FILE_FORMATTER[0]["kwargs"])

    lHandler.setFormatter(formatter)    
    lHandler.propagate = True

    if filter is not None:
        lHandler.addFilter(filter)

    G_ACTIVE_HANDLERS.append(lHandler)
    _refreshQueueListener()

# ==================================================================================
def removeFileHandler(name: str) -> None:
    global G_ACTIVE_HANDLERS
    if name in G_ACTIVE_HANDLERS:
        G_ACTIVE_HANDLERS.remove(name)
        _refreshQueueListener()
        
# ==================================================================================
def setNamespaceLevel(namespace: str, level: int) -> None:
    NamespaceFilter.setNSLogLevel(namespace, level)

# ==================================================================================
def stopLogging():
    global G_LOG_LISTENER
    if G_LOG_LISTENER is not None:
        G_LOG_LISTENER.stop()