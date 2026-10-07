# ==================================================================================
from asyncio import AbstractEventLoop, Task, get_running_loop, to_thread
from asyncio import run as asyncioRun
from inspect import iscoroutinefunction
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
    C_DEFAULT_STOP_TIMEOUT: float = 5.0

    def __init__(self, work: Callable[..., Awaitable], name: str | None = None) -> None:
        if work is None or not iscoroutinefunction(work):
            raise TypeError("AsyncProcess requires an awaitable (coroutine function) work argument")

        self._work: Callable[..., Awaitable] = work
        self._name: str = name or getRandomName()
        self._process: Process | None = None
        self._shutdownEvent: SyncEvent | None = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def isRunning(self) -> bool:
        return self._process is not None and self._process.is_alive()

    # Intentionally left as a stub for IntelliSense / type-checker signature
    async def work(self, shutdownEvent: SyncEvent, *args, **kwargs): ...

    def _assertStartReady(self) -> None:
        if self._process is not None:
            if self._process.is_alive():
                raise RuntimeError(f"Service '{self._name}' is already running.")
            self._process.close()
            self._process = None
            self._shutdownEvent = None

    def _assertStopReady(self) -> None:
        if self._process is None or not self._process.is_alive():
            raise RuntimeError(f"Service '{self._name}' is not running.")

    def start(self, *args, **kwargs) -> None:
        self._assertStartReady()
        self.raiseEvent("ON_STARTING")

        lShutdownEvent: SyncEvent = Event()

        def _processEntry(shutdownEvent: SyncEvent, *args, **kwargs) -> None:
            async def _runner() -> None:
                await self.asyncRaiseEvent("ON_STARTED")
                try:
                    await self._work(shutdownEvent, *args, **kwargs)
                finally:
                    await self.asyncRaiseEvent("ON_STOPPED")

            asyncioRun(_runner())

        lProcess = Process(
            target=_processEntry,
            args=(lShutdownEvent, *args),
            kwargs=kwargs,
            daemon=True,
            name=self._name,
        )
        lProcess.start()

        self._process = lProcess
        self._shutdownEvent = lShutdownEvent

    async def _stopAsync(self, timeout: float = C_DEFAULT_STOP_TIMEOUT, forced: bool = False) -> None:
        if self._shutdownEvent is not None:
            self._shutdownEvent.set()

        lProcess = self._process
        if lProcess is None:
            return

        if lProcess.is_alive():
            if forced:
                lProcess.terminate()

            await to_thread(lProcess.join, timeout)

            if lProcess.is_alive():
                lProcess.kill()
                await to_thread(lProcess.join, 1.0)

        lProcess.close()
        self._process = None
        self._shutdownEvent = None

    def stop(self, timeout: float = C_DEFAULT_STOP_TIMEOUT, forced: bool = False) -> None:
        self._assertStopReady()
        self.raiseEvent("ON_STOPPING")

        try:
            lLoop: AbstractEventLoop = get_running_loop()
        except RuntimeError:
            # No running event loop – perform stop synchronously
            if self._shutdownEvent is not None:
                self._shutdownEvent.set()

            lProcess = self._process
            if lProcess is not None:
                if not forced:
                    lProcess.join(timeout)

                # Forced termination if the process is still alive after the timeout
                if lProcess.is_alive():
                    lProcess.terminate()
                    lProcess.join(timeout)

                    if lProcess.is_alive():
                        lProcess.kill()
                        lProcess.join(1.0)

                lProcess.close()

            self._process = None
            self._shutdownEvent = None
            self.raiseEvent("ON_STOPPED")
            return

        lTask: Task = lLoop.create_task(
            self._stopAsync(timeout=timeout, forced=forced)
        )

        def _onDone(t: Task) -> None:
            try:
                t.result()
            except Exception:
                pass
            self.raiseEvent("ON_STOPPED")

        lTask.add_done_callback(_onDone)


# ==================================================================================
__all__ = ["AsyncProcess"]
