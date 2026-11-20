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
    def __init__(self, process: Process, expiry: float = 0.1):         
        super().__init__()
        self._expiry: int = int(expiry * 1e9) # converts expiry into nanoseconds
        self._process: Process = process
        self._identity: int = process.ident

        self.Properties.extend(["identity"])
        self._clientState: eClientState = eClientState.PENDING
        self._expiryTask: Optional[Task] = None    

    def beat(self, expiry: float = 0.1):
        self._expiry = int(expiry * 1e9) + monotonic_ns()

        if self._expiryTask is not None and not self._expiryTask.done():
            self._expiryTask.cancel()
            self._expiryTask = None

        self._clientState = eClientState.ACTIVE

        async def _onExpiry():
            self._clientState = eClientState.DORMANT
        
        expiryTask: Task = createTask(asyncSleep, float(self._expiry / 1e9))
        expiryTask.add_done_callback(_onExpiry)
        

    @property
    def process(self) -> Process:
        return self._process
        
    @property
    def identity(self) -> int:
        return self._identity

    @property
    def expiry(self) -> int:
        return self._expiry
