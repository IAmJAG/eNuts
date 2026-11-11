# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import AbstractEventLoop, Task, get_running_loop, to_thread
from asyncio import run as asyncioRun
from inspect import iscoroutinefunction
from multiprocessing import Event, Process
from multiprocessing.synchronize import Event as SyncEvent
from typing import Any, Awaitable, Callable

# ==================================================================================
from jAGFx.names import getRandomName

# ==================================================================================
from ..types.interface.services import iService
from .__subscription import AsyncSubscription

# ==================================================================================
C_DEFAULT_STOP_TIMEOUT: float = 3.0
# ==================================================================================

# ==================================================================================
def _processEntry(func: Callable[..., Awaitable], shutdownEvent: SyncEvent, args, kwargs) -> None:
    async def _runner() -> None:

        # Intentionally left as a stub for IntelliSense / type-checker signature
        def work(shutdownEvent: SyncEvent, *args, **kwargs):...
        work: Callable[..., Awaitable] = func

        await work(shutdownEvent, *args, **kwargs)

    asyncioRun(_runner())

# ==================================================================================
class AsyncProcess(AsyncSubscription, iService):
    def __init__(self, work: Callable[..., Awaitable], name: str | None = None) -> None:
        super().__init__()
        if work is None or not iscoroutinefunction(work):
            raise TypeError("AsyncProcess requires an awaitable (coroutine function) work argument")

        self._work: Callable[..., Awaitable] = work
        
        self._process: Process | None = None
        self._shutdownEvent: SyncEvent | None = None

        self._name: str = name or getRandomName()

    @property
    def name(self) -> str:
        return self._name

    @property
    def isRunning(self) -> bool:
        return self._process is not None and self._process.is_alive()

    # Intentionally left as a stub for IntelliSense / type-checker signature
    async def _work(self, shutdownEvent: SyncEvent, *args, **kwargs): ...

    def _assertStartReady(self) -> None:
        if self._process is not None:
            if self._process.is_alive():
                message: str = f"Service '{self._name}' is already running."
                raise RuntimeError(message)
            
            self._process.close()
            self._process = None
            self._shutdownEvent = None

    def _assertStopReady(self) -> None:        
        if self._process is None:
            message = f"Service '{self._name}' is not running."
            raise RuntimeError(message)

    async def _asyncStop(self, timeout: float = C_DEFAULT_STOP_TIMEOUT, forced: bool = False) -> None:        
        if self._shutdownEvent is not None: 
            self._shutdownEvent.set()
        
        process = self._process
        if process is None: return

        if process.is_alive():
            if forced:
                process.terminate()

            await to_thread(process.join, timeout)

            if process.is_alive():
                process.kill()
                await to_thread(process.join, 1.0)

        process.close()
        self._process = None
        self._shutdownEvent = None   

    async def asyncStop(self, timeout: float = C_DEFAULT_STOP_TIMEOUT, forced: bool = False) -> None:
        self._assertStopReady()

        def asyncStop(timeout: float, forced: bool): ...
        asyncStop: Callable[..., Awaitable] = self._asyncStop

        self.raiseEvent("ON_STOPPING")
        try:
            await asyncStop(timeout=timeout, forced=forced)

        finally:
            self._process = None
            self._shutdownEvent = None
            self.raiseEvent("ON_STOPPED")

    def _syncStop(self, timeout: float = C_DEFAULT_STOP_TIMEOUT, forced: bool = False) -> None:
        try:
            if self._shutdownEvent is not None:
                self._shutdownEvent.set()

            process = self._process
            if process is not None:
                if not forced:
                    process.join(timeout)

                if process.is_alive():
                    process.terminate()
                    process.join(timeout)

                    if process.is_alive():
                        process.kill()
                        process.join(1.0)

                process.close()

        except Exception:
            raise

    def stop(self, timeout: float = C_DEFAULT_STOP_TIMEOUT, forced: bool = False) -> None:
        self._assertStopReady()
        self.raiseEvent("ON_STOPPING")

        try:
            loop: AbstractEventLoop = get_running_loop()

        except RuntimeError:
            self._syncStop(timeout=timeout, forced=forced)
            return

        task: Task = loop.create_task(
            self._syncStop(timeout=timeout, forced=forced)
        )

        def _onDone(t: Task) -> None:
            self.raiseEvent("ON_STOPPED")

        task.add_done_callback(logTaskException)
        task.add_done_callback(_onDone)

    def start(self, *args, **kwargs) -> None:
        self._assertStartReady()

        self.raiseEvent("ON_STARTING")
        shutdownEvent: SyncEvent = Event()
        name: str = self._name
        
        # Intentionally left as a stub for IntelliSense / type-checker signature
        async def work(shutdownEvent: SyncEvent, *args, **kwargs): ...
        work: Callable[..., Awaitable] = self._work

        process = Process(
            target=_processEntry, args=(work, shutdownEvent, args, kwargs),
            daemon=True, name=name,
        )
        process.start()

        self._process = process
        self._shutdownEvent = shutdownEvent

# ==================================================================================
__all__ = ["AsyncProcess"]
