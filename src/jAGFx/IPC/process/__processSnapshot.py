# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import Task, current_task
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
    def __init__(self, process: Process, expiry: float = 0.1):         
        Serializable.__init__(self)
        Subscription.__init__(self)
        self._expiry: int = int(expiry * 1e9)  + monotonic_ns() # converts expiry into nanoseconds
        self._process: Process = process
        self._identity: int = process.ident

        self.Properties.extend(["identity"])
        self._clientState: eClientState = eClientState.PENDING
        self._expiryTask: Optional[Task] = None    

    def beat(self, expiry: float = 0.1) -> None:
        durationNs: int = int(expiry * 1e9)
        now: int = monotonic_ns()

        self._expiry = now + durationNs

        if self._expiryTask is not None:
            self._expiryTask.cancel()

        def _expire(task: Task) -> None:
            if self._expiryTask is task:
                self._clientState = eClientState.DORMANT

        self._clientState = eClientState.ACTIVE

        expiryTask: Task = createTask(asyncSleep, expiry)
        expiryTask.add_done_callback(_expire)
        self._expiryTask = expiryTask
        

    @property
    def process(self) -> Process:
        return self._process
        
    @property
    def identity(self) -> int:
        return self._identity

    @property
    def expiry(self) -> int:
        return self._expiry
