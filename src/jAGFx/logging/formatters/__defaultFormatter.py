# ==================================================================================
import inspect
from logging import Formatter

# ==================================================================================
import colorlog

# ==================================================================================
from utilities import getCallersFrame

# ==================================================================================
from ..data import CallerInformation

fmtList = [
    "%(light_black)s[%(asctime)s]%(reset)s",
    "%(log_color)s[%(levelname)-8s]%(reset)s ",    
    "%(message_log_color)s%(message)s%(reset)s",
]
# "%(log_color)s[%(caller)-8s]%(reset)s ",
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


# ==================================================================================
class DefaultFormatter(Formatter):
    def __init__(self, fmt=None, datefmt=None, style="%", validate=True):
        super().__init__(fmt, datefmt, style, validate)
        lFormatter: colorlog.ColoredFormatter = colorlog.ColoredFormatter(
                fmt=C_LOG_FORMAT,
                datefmt="%Y%m%d %H%M%S",
                log_colors=C_LOG_COLORS,
                secondary_log_colors=C_SECONDARY_COLORS,
            )
        self._coloredFormatter = lFormatter

    def format(self, record):
        try:
            coloredFormatter: colorlog.ColoredFormatter = self._coloredFormatter
            lCaller = getattr(record, "caller", None)
            if lCaller is None:
                lCaller = CallerInformation("", "", "NOT", "MINE", "", 0)
                setattr(record, "caller", lCaller)

            lOMsg = record.msg
            lLines = str(lOMsg).splitlines()

            record.msg = lLines[0]
            lFormattedParts = [coloredFormatter.format(record)]            
            for i in range(1, len(lLines)):
                record.msg = f"{TAB}{lLines[i]}"
                lFormattedParts.append(f"{coloredFormatter.format(record)}")

            record.msg = lOMsg
            return LF.join(lFormattedParts)

        except Exception:
            raise
