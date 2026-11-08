# ==================================================================================================
from fluxCore.types import eTimeDeltaFormat


# ==================================================================================================
def fromNanoSeconds(nanoseconds: int, tdf: eTimeDeltaFormat = eTimeDeltaFormat.NANOSECONDS) -> float:
    if tdf == eTimeDeltaFormat.MILLISECONDS:
        return nanoseconds / 1e6

    if tdf == eTimeDeltaFormat.MICROSECONDS:
        return nanoseconds / 1e3

    if tdf == eTimeDeltaFormat.SECONDS:
        return nanoseconds / 1e9
    
    return nanoseconds