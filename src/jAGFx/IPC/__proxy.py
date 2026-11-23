# ==================================================================================
from __future__ import annotations

# ==================================================================================
import inspect

from ..types.interface.communication import iProxy

# ==================================================================================
from .__processHost import ProcessHost


# ==================================================================================
class Proxy(iProxy):
    def __init__(self, identity: int, host: ProcessHost, *args, **kwargs):
        super().__init__(*args, *kwargs)
        if not self._isCalledFromAllowedFactory():
            raise RuntimeError(
                "ProcessHost can only be created inside ProcessHost.start."
            )

        self._host: ProcessHost = host
        self._identity: int = identity


    @property
    def identity(self) -> int:
        return self._identity

    @staticmethod
    def _isCalledFromAllowedFactory():
        frame = inspect.currentframe()
        try:
            # Frame 0: _isCalledFromAllowedFactory
            # Frame 1: ClassA.__init__
            # Frame 2: actual caller of ClassA(...)
            callerFrame = frame.f_back.f_back if frame and frame.f_back else None
            if callerFrame is None: return False

            functionName = callerFrame.f_code.co_name
            classArg = type(callerFrame.f_locals.get("self"))
            return functionName == "start" and classArg is ProcessHost
        
        finally:
            del frame
