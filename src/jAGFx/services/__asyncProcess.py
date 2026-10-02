# ==================================================================================
from asyncio import AbstractEventLoop, Task, get_running_loop, to_thread
from multiprocessing import Event, Process
from multiprocessing.synchronize import Event as SyncEvent
from typing import Awaitable, Callable

# ==================================================================================
from jAGFx.names import getRandomName

# ==================================================================================
from ..types.interface.services import iService
from .__subscription import AsyncSubscription


# ==================================================================================
class AsyncProcess(iService, AsyncSubscription):
    def __init__(self, work: Callable[..., Awaitable], name: str | None = None) -> None:
        self.work: Callable[..., Awaitable] = work
        self._name: str = name or getRandomName()
        self._process: Process | None = None
        self._shutdownEvent: SyncEvent | None = None

    @property
    def name(self):
        return self._name

    @property
    def isRunning(self) -> bool:
        return self._process is not None and self._process.is_alive()

    async def work(self, shutdownEvent: SyncEvent, *args, **kwargs): ...

    def _assertStartReady(self):
        if self._process is not None:
            if self._process.is_alive(): 
                raise RuntimeError(f"Service '{self._name}' is already running.")                
            
            self._process.close()
            self._process = None

    def _assertStopReady(self):
        if self._process is None:
            raise RuntimeError(f"Service '{self._name}' is not running.")

        if not self._process.is_alive():
            raise RuntimeError(f"Service '{self._name}' is not running.")

        process: Process | None = self._process
        if process is None or not process.is_alive():
            self._shutdownEvent = None
            self._process = None

    def start(self, *args, **kwargs):
        self._assertStartReady()
        self.raiseEvent("ON_STARTING")

        lShutdownEvent: SyncEvent = Event()
        async def work(_shutdownEvent: SyncEvent, *args, **kwargs): 
            await self.raiseEvent("ON_STARTED")
            await self.work(_shutdownEvent, *args, **kwargs)
            await self.raiseEvent("ON_STOPPED")
        
        process = Process(
            target=work, args=(lShutdownEvent, *args),
            kwargs=kwargs, daemon=True, name=self._name,
        )
        process.start()

        self._process = process
        self._shutdownEvent = lShutdownEvent

    async def _stopAsync(self, timeout: float = 0.01, forced: bool = False):
        self._assertStopReady()

        self._shutdownEvent.set()

        process: Process | None = self._process        
        if process.is_alive():
            if forced:  process.terminate()
            await to_thread(process.join, timeout)

    def stop(self, timeout: float = 0.01, forced: bool = False) -> None:
        self._assertStopReady()

        self.raiseEvent("ON_STOPPING")
        if self._process is None:
            self._shutdownEvent = None
            return

        try:
            loop: AbstractEventLoop = get_running_loop()

        except RuntimeError:
            if self._shutdownEvent is not None: self._shutdownEvent.set()

            process: Process | None = self._process            
            if process is None: return

            process.join(timeout)
            if process.is_alive():                
                if forced: 
                    process.terminate()
                    
                process.join(timeout)                
                
            self._shutdownEvent = None
            self._process = None            
            self.raiseEvent("ON_STOPPED")
            return
            

        task: Task = loop.create_task(self._stopAsync(timeout=timeout, forced=forced))
        task.add_done_callback(lambda: self.raiseEvent("ON_STOPPED"))
