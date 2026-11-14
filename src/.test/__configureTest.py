# ==================================================================================
from __future__ import annotations

# ==================================================================================
import __monkeyPatch

# ==================================================================================
from jAGFx.logging import TRACE, suppressedLogger
from utilities import THIRD_PARTY_LOG_LEVEL, THIRD_PARTY_LOGGERS


# ==================================================================================
def setupLogging(name: str = "", level: int = TRACE) -> None:
    setupLogging(name, level)
    suppressedLogger(THIRD_PARTY_LOGGERS, THIRD_PARTY_LOG_LEVEL)
