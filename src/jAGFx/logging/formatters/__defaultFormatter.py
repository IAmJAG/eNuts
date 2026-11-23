# ==================================================================================
from logging import Formatter

# ==================================================================================
import colorlog

from .. import __utilities

# ==================================================================================
from ..data import CallerInformation

G_LOG_FORMAT = [
    "%(light_black)s[%(asctime)s]%(reset)s",
    "%(log_color)s[%(levelname)-8s]%(reset)s ",
    "%(message_log_color)s[%(domain)-8s]%(reset)s ",
    "%(message_log_color)s[%(member)-8s]%(reset)s ",
    "%(message_log_color)s%(message)s%(reset)s",
]
G_LOG_FORMAT = "".join(G_LOG_FORMAT)
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


# ==================================================================================
class DefaultFormatter(Formatter):
    """Colored formatter for console output only."""

    def __init__(self, fmt=None, datefmt=None, style="%", validate=True):
        super().__init__(fmt, datefmt, style, validate)
        lFormatter: colorlog.ColoredFormatter = colorlog.ColoredFormatter(
            fmt=G_LOG_FORMAT,
            datefmt="%Y%m%d %H%M%S",
            log_colors=C_LOG_COLORS,
            secondary_log_colors=C_SECONDARY_COLORS,
        )
        self._coloredFormatter = lFormatter

    def format(self, record):
        try:
            coloredFormatter: colorlog.ColoredFormatter = self._coloredFormatter
            caller: CallerInformation = getattr(record, "caller", None)
            if caller is None:
                caller = CallerInformation("", "", "NOT", "MINE", "", -1)
                setattr(record, "caller", caller)

            lOMsg = record.msg
            lLines = [ln for ln in str(lOMsg).splitlines() if ln.strip()]

            if not lLines:
                return ""

            record.msg = lLines[0]
            lFormattedParts = [coloredFormatter.format(record)]
            for i in range(1, len(lLines)):
                record.msg = f"{TAB}{lLines[i]}"
                lFormattedParts.append(coloredFormatter.format(record))

            record.msg = lOMsg
            return LF.join(lFormattedParts)

        except Exception:
            raise


# ==================================================================================
class FileFormatter(Formatter):
    """Plain (non-colored) formatter for file handlers.

    - Never emits ANSI escape sequences.
    - Skips empty / whitespace-only lines so the log file stays clean.
    """

    def __init__(self, fmt=None, datefmt=None, style="%", validate=True):
        # Default plain format matching the previous DEF_FILE_FORMATTER intent
        if fmt is None:
            fmt = "[{asctime}][{levelname:<8}] [{domain}] [{member}] {message}"
            style = "{"
        if datefmt is None:
            datefmt = "%Y%m%d %H%M%S"
        super().__init__(fmt, datefmt, style, validate)

    def format(self, record):
        try:
            caller: CallerInformation = getattr(record, "caller", None)
            if caller is None:
                caller = CallerInformation("", "", "NOT", "MINE", "", -1)
                setattr(record, "caller", caller)

            # Ensure domain / member exist for the format string
            if not hasattr(record, "domain"):
                setattr(record, "domain", getattr(caller, "klass", None) or getattr(caller, "module", ""))
            if not hasattr(record, "member"):
                setattr(record, "member", getattr(caller, "member", ""))

            lOMsg = record.msg
            lLines = [ln for ln in str(lOMsg).splitlines() if ln.strip()]

            if not lLines:
                return ""  # signal to handler that nothing should be written

            record.msg = lLines[0]
            lFormattedParts = [super().format(record)]
            for i in range(1, len(lLines)):
                record.msg = f"{TAB}{lLines[i]}"
                lFormattedParts.append(super().format(record))

            record.msg = lOMsg
            result = LF.join(lFormattedParts)
            return result.rstrip()  # never end with extra blank line

        except Exception:
            raise
