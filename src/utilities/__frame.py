# ==================================================================================================
from inspect import FrameInfo, currentframe, getframeinfo, getmodule
from os.path import abspath, basename
from traceback import FrameSummary, format_exception

# ==================================================================================================
from types import FrameType, ModuleType
from typing import Any, Dict, List, Set

# ==================================================================================================
IGNORE_MODULES = (
    "builtins",
    "__builtin__",
    "importlib",
    "_frozen_importlib",
    "jAGFx.logging",
)
# ==================================================================================================

# ==================================================================================================
def getCallersFrame(frame: FrameType = None, otherIgnoreModules: Set = set()) -> FrameType:
    # Get the caller's frame - which is one step above the current frame
    frame = frame or currentframe().f_back 
    lThisFile = abspath(__file__)

    while frame:
        lFrameInfo: FrameInfo = getframeinfo(frame)
        lFrameFile: str = abspath(lFrameInfo.filename)

        lModule: ModuleType = getmodule(frame)
        lModuleName: str = lModule.__name__ if lModule else None

        IsThisFile = lFrameFile == lThisFile
        IsBuiltIn: bool = lModuleName.startswith(IGNORE_MODULES) or lFrameInfo.filename.startswith("<")        

        if not IsThisFile and not IsBuiltIn: 
            return frame
        
        if frame.f_back is None: 
            return frame
        
        return getCallersFrame(frame.f_back, otherIgnoreModules)

    return None

# ==================================================================================================
def FormatFrame(frame: FrameSummary, fullfilename: bool = False) -> str:
    if fullfilename:
        return f"{frame.filename} in {frame.name} at line {frame.lineno}"    
    return f"{basename(frame.filename)} in {frame.name} at line {frame.lineno}"

# ==================================================================================================
def getFrameInfo(frame: FrameType): 
    return {
        "File": frame.f_code.co_filename or "",
        "Package": frame.f_globals["__package__"] or "",
        "Module": frame.f_globals["__name__"] or "",
        "Class": frame.f_locals.get("__class__", None).__name__ if frame.f_locals.get("__class__", None) else "" or "",
        "Member": frame.f_code.co_name or "",
        "LineNo": frame.f_lineno or -1,
    }

# ==================================================================================================
def getCallableFromFrame(frame: FrameType):
    name = frame.f_code.co_name    
    if name in frame.f_locals: return frame.f_locals[name]
    if "self" in frame.f_locals:
        obj = frame.f_locals["self"]
        member = getattr(obj.__class__, name, None)
        if member is None: return member
        if isinstance(member, property): return member
        return getattr(obj, name, None)
    return frame.f_globals.get(name, None)

# ==================================================================================================
def formatTrace(err) -> List[str]:
    """Return stack-trace lines for any exception.

    Prefer a custom getTrace() when present; otherwise use stdlib traceback.
    Always returns a list (never None) so callers can safely extend.
    """
    try:
        if hasattr(err, "getTrace"):
            lTrace: Dict[str, Any] = err.getTrace()

            traceStr: List[str] = []
            traceStr.append(f"{TAB}{lTrace['Message']}:")
            traceStr.append(f"{TAB}Process: {lTrace['Origin']['Process']}")
            traceStr.append(f"{TAB}Thread: {lTrace['Origin']['ThreadId']} -> {lTrace['Origin']['ThreadName']}")
            traceStr.append(f"{LF}{TAB}Sources:")
            for origins in lTrace["Sources"]:
                if origins["File"].endswith("__init__.py") or origins["Package"].endswith(IGNORE_MODULES):
                    continue
                traceStr.append(f"{TAB * 2}{origins['File']}:{origins['LineNo']}")

            return traceStr

        # Standard Exception path — always emit a usable traceback
        lLines: List[str] = format_exception(type(err), err, err.__traceback__)
        # strip trailing newlines so the formatter can re-join cleanly
        return [line.rstrip("\n") for line in lLines if line.strip()]

    except Exception as ex:
        raise ex
