# ==================================================================================================
from logging import DEBUG, ERROR, INFO, WARNING, getLogger
from re import Pattern, compile
from typing import List

# ==================================================================================================
ANSI_RE = compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
# ==================================================================================================

# ==================================================================================================
THIRD_PARTY_LOG_LEVEL: int = WARNING
THIRD_PARTY_LOGGERS: List[str] = [
    "asyncio",
    "adbutils.sync",
    "qasync._QEventLoop",
    "asyncio.windows_events",
    "qasync._windows._EventPoller",
    "qasync._windows._EventWorker",
    "qasync._windows._IocpProactor",
    "qasync.QThreadExecutor",
    "qasync._QThreadWorker",
]
# ==================================================================================================

# ==================================================================================================
def StripAnsi(text):   
    return ANSI_RE.sub("", text) if isinstance(text, str) else text
