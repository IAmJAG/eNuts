# ==================================================================================
from logging import Formatter

# ==================================================================================
from ..data import CallerInformation


# ==================================================================================
class DefaultFormatter(Formatter):
    def format(self, record):
        try:
            lCaller = getattr(record, "caller", None)
            if lCaller is None:
                lCaller = CallerInformation("", "", "NOT", "MINE", "", 0)
                setattr(record, "caller", lCaller)

            lOMsg = record.msg
            lLines = str(lOMsg).splitlines()

            record.msg = lLines[0]
            lFormattedParts = [super().format(record)]

            for i in range(1, len(lLines)):
                record.msg = f"{TAB}{lLines[i]}"
                lFormattedParts.append(f"{super().format(record)}")

            record.msg = lOMsg
            return LF.join(lFormattedParts)

        except Exception:
            raise
