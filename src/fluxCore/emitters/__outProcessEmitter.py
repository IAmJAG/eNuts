# ==================================================================================
from __future__ import annotations

# ==================================================================================
import os

# ==================================================================================
from asyncio import Event as asyncEvent
from asyncio import Future, Task, gather
from multiprocessing import Queue

# ==================================================================================
from typing import List, Optional

# ==================================================================================
from jAGFx.services import AsyncProcess

# ==================================================================================
from ..devices import SCRCPY
from ..types.interface.emitters import iSCRCPYEmitter
from .__SCRCPYOptions import SCRCPYOptions


# ==================================================================================
class OPEmitter(SCRCPY, AsyncProcess, iSCRCPYEmitter):
    def __init__(self, serial: str, name: str | None = None, options: SCRCPYOptions | None = None) -> None:
        SCRCPY.__init__(self, serial=serial, name=name)
        AsyncProcess.__init__(self, work=self.work, name=name)
        self._tasks: List[Future] = None
    
    async def _receiver(self, shutdownEvent: asyncEvent, queue: Queue) -> iSCRCPYEmitter:
        def isShuttingDown() -> bool: ...
        isShuttingDown = shutdownEvent.is_set
        while not isShuttingDown(): 
            msg: str = queue.get()
            print(msg)

    async def _dispatch(self, msg: str) -> None:
        self._outQueue.put(msg)
            
    async def work(self, shutdownEvent: asyncEvent, inQueue: Queue, outQueue: Queue, *args, **kwargs) -> None:        
        self._outQueue = outQueue

        tasks: List[Task] = [
            self._receiver(shutdownEvent, inQueue),
        ]
        self._tasks = gather(*tasks)

        try:
            await shutdownEvent.wait()

        finally:
            for task in self._tasks:
                task.cancel()


    def start(self, *args, **kwargs):
        inQueue: Queue = Queue()
        outQueue: Queue = Queue()
        super().start(inQueue=outQueue, outQueue=inQueue, *args, **kwargs)

        tasks: List[Task] = [
            self._receiver(self._shutdownEvent, inQueue),
        ]

        self._tasks = gather(*tasks)