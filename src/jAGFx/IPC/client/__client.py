# ==================================================================================
from __future__ import annotations

# ==================================================================================
import inspect

# ==================================================================================
from asyncio import Task
from asyncio import sleep as asyncSleep
from time import monotonic_ns
from typing import Optional

# ==================================================================================
from ...serializer import Serializable
from ...services import Subscription
from ...types import eClientState
from ...types.interface.communication import iProcessHost
from ...types.interface.communication.client import iClient


# ==================================================================================
class Client(iClient, Subscription):
    def __init__(self, clientId: int, expiry: float = 0.1):         
        super().__init__()
        if not self._isCalledFromAllowedFactory():
            raise RuntimeError("ProcessHost can only be created inside ProcessHost.start.")
        
        self._expiry: int = int(expiry * 1e9)  + monotonic_ns() # converts expiry into nanoseconds
        self._identity: int = clientId
        
        self._clientState: eClientState = eClientState.PENDING
        self._expiryTask: Optional[Task] = None        

    def beat(self, expiry: float = 0.1) -> None:
        # Add a small margin so the next heartbeat can arrive before this one expires
        # even under modest queue / scheduling latency.
        MARGIN: float = 0.15
        safeExpiry: float = max(0.05, expiry + MARGIN)

        durationNs: int = int(safeExpiry * 1e9)
        now: int = monotonic_ns()

        self._expiry = now + durationNs
        
        # Cancel previous expiry (its done callback must be ignored)
        oldTask: Optional[Task] = self._expiryTask
        if oldTask is not None and not oldTask.done():
            self._expiryTask = None
            oldTask.cancel()

        def _expire(task: Task) -> None:
            # Ignore cancelled tasks and any task that is no longer current
            if task.cancelled() or task is not self._expiryTask:
                return
            trace("Heartbeat expired")
            self.clientState = eClientState.DORMANT

        newTask: Task = createTask(asyncSleep, safeExpiry)
        newTask.add_done_callback(_expire)
        self._expiryTask = newTask
        self.clientState = eClientState.ACTIVE

    @property
    def clientState(self) -> eClientState:
        return self._clientState

    @clientState.setter
    def clientState(self, value: eClientState):
        assert isinstance(value, eClientState)
        if self._clientState != value:
            oldValue: eClientState = self._clientState
            self._clientState = value
            trace(f"State changed from {oldValue.name} to {value.name}")
            self.raiseEvent("STATE_CHANGED", value, oldValue)
        
    @property
    def identity(self) -> int:
        return self._identity

    @property
    def expiry(self) -> int:
        return self._expiry
        
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
            return functionName == "start" and isinstance(classArg, iProcessHost)
        
        finally:
            del frame
