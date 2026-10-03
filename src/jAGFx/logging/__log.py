# ==================================================================================
from logging import log as LOG
from threading import RLock
from types import FrameType
from typing import Dict, List, Set, Tuple

# ==================================================================================
from utilities import StripAnsi, formatTrace, getCallersFrame, getFrameInfo

# ==================================================================================
from ..types import isListOfT
from .data import CallerInformation

# ==================================================================================
LOGLOCK: RLock = RLock()

# ==================================================================================
def _log(messages: List[str] | str, level: int, extra: Dict):
    if not isListOfT(messages, str) and not isinstance(messages, str):
        raise TypeError(f"Expected an string or list of strings got {type(messages).__name__}.")

    with LOGLOCK:
        try:
            messages = StripAnsi(messages) if isinstance(messages, str) else [StripAnsi(message) for message in messages]
            LOG(level, LF.join(messages), extra=extra)

        except Exception as ex:
            raise ex

# ==================================================================================
def log(
    messages: str | List[str] | Tuple[str] | Dict[str, str] | Set[str],
    level: int, err: Exception = None, frame: FrameType = None,
) -> None:    
    if frame is None: frame = getCallersFrame()        
    if frame is None: raise ValueError("Could not determine caller's frame.")
    
    lFrameInfo = getFrameInfo(frame)    
    lCallerInfo = CallerInformation(**lFrameInfo)

    lExtra: Dict[str, CallerInformation] = dict[str, CallerInformation]({"caller": lCallerInfo})

    if isinstance(messages, str): messages = [messages]    
    if isinstance(messages, Tuple): messages = list(messages)
    if isinstance(messages, Dict): messages = [
        f"{key}: {value}" for key, value in messages.items()
    ] 
    if isinstance(messages, Set): messages = list(messages)    
    if err is not None:
        lTraceLines = formatTrace(err)
        if lTraceLines:
            messages.extend(lTraceLines)

    _log(messages, level, lExtra)
