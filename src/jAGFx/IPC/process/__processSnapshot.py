# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import Task
from asyncio import sleep as asyncSleep
from multiprocessing import Process
from time import monotonic_ns
from typing import Optional

# ==================================================================================
from ...serializer import Serializable
from ...services import Subscription
from .__eClientState import eClientState


# ==================================================================================
class ProcessSnapshot(Serializable, Subscription):
    def __init__(self, processId: int, expiry: float = 0.1):         
        Serializable.__init__(self)
        Subscription.__init__(self)
        self._expiry: int = int(expiry * 1e9)  + monotonic_ns() # converts expiry into nanoseconds
        self._identity: int = processId

        self.Properties.extend(["identity"])
        self._clientState: eClientState = eClientState.PENDING
        self._expiryTask: Optional[Task] = None    

    def beat(self, expiry: float = 0.1) -> None:
        durationNs: int = int(expiry * 1e9)
        now: int = monotonic_ns()

        self._expiry = now + durationNs

        expiryTask: Optional[Task] = self._expiryTask
        if expiryTask is not None and not expiryTask.done():
            self._expiryTask = None
            expiryTask.cancel()

        def _expire(task: Task) -> None:
            if self._expiryTask is not None:
                self.clientState = eClientState.DORMANT
        
        expiryTask = createTask(asyncSleep, expiry)
        expiryTask.add_done_callback(_expire)
        self._expiryTask = expiryTask
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
            self.raiseEvent("STATE_CHANGED", value, oldValue)
        
    @property
    def identity(self) -> int:
        return self._identity

    @property
    def expiry(self) -> int:
        return self._expiry
