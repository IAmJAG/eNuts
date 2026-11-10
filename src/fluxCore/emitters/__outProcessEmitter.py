# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import CancelledError, Future, gather, to_thread
from asyncio import sleep as asyncSleep
from multiprocessing import Queue
from multiprocessing.synchronize import Event as syncEvent
from queue import Empty

# ==================================================================================
from typing import Optional

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
        self._tasks: Optional[Future] = None
    
    async def _receiver(self, shutdownEvent: syncEvent, queue: Queue) -> None:
        def isShuttingDown() -> bool: ...
        isShuttingDown = shutdownEvent.is_set
        
        while not isShuttingDown():
            try:
                msg: str = queue.get_nowait()
                print(msg)

            except Empty:
                await asyncSleep(0.01)

    async def _dispatch(self, msg: str) -> None:
        self._outQueue.put(msg)
            
    async def work(self, shutdownEvent: syncEvent, inQueue: Queue, outQueue: Queue, *args, **kwargs) -> None:        
        self._outQueue = outQueue
        self._tasks = gather(
            self._receiver(shutdownEvent, inQueue),
        )

        async def waitForShutdown() -> None: 
            await to_thread(shutdownEvent.wait)

        try:
            await waitForShutdown()

        finally:
             if self._tasks is not None:
                self._tasks.cancel()

                try:
                    await self._tasks

                except CancelledError:
                    pass

                self._tasks = None


    def start(self, *args, **kwargs):
        inQueue: Queue = Queue()
        outQueue: Queue = Queue()
        super().start(inQueue=outQueue, outQueue=inQueue, *args, **kwargs)

        self._tasks = gather(
            self._receiver(self._shutdownEvent, inQueue),
        )