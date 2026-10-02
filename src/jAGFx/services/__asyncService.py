# ==================================================================================
from asyncio import CancelledError, Event, Task, get_running_loop
from asyncio import sleep as asyncSleep
from inspect import iscoroutinefunction
from typing import Awaitable, Callable

# ==================================================================================
from jAGFx.names import getRandomName

# ==================================================================================
from ..types.interface.services import iService
from .__subscription import AsyncSubscription


# ==================================================================================
class AsyncService(iService, AsyncSubscription):
    """Run one asynchronous unit of work as a managed asyncio task."""

    C_DEFAULT_FORCE_AFTER: float = 0.1

    def __init__(
        self, work: Callable[..., Awaitable] | None = None,
        name: str | None = None, throttle: float = 0.0
    ) -> None:
        if throttle < 0.0:
            raise ValueError("throttle must be greater than or equal to zero")

        if work is not None and not iscoroutinefunction(work):
            raise TypeError("AsyncService requires an awaitable (coroutine function) work argument")

        self.work: Callable[..., Awaitable] | None = work
        self._name: str = name or getRandomName()
        self._isRunning: bool = False
        self._isStopping: bool = False
        self._pauseEvent: Event = Event()
        self._pauseEvent.set()
        self._task: Task[None] | None = None
        self._throttle: float = throttle

    @property
    def name(self) -> str:
        return self._name

    @property
    def isRunning(self) -> bool:
        return self._isRunning

    @property
    def isPaused(self) -> bool:
        return self._isRunning and not self._pauseEvent.is_set()

    @property
    def task(self) -> Task[None] | None:
        return self._task

    # Intentionally left as a stub for IntelliSense / type-checker signature
    async def work(self, *args, **kwargs): ...

    def _assertStartReady(self) -> None:
        if self._isRunning:
            raise RuntimeError(f"Service '{self._name}' is already running.")
        if self._isStopping:
            raise RuntimeError(f"Service '{self._name}' is stopping.")
        if self.work is None or not iscoroutinefunction(self.work):
            raise TypeError("AsyncService requires an awaitable (coroutine function) work argument")

    def _assertStopReady(self) -> None:
        if not self._isRunning and self._task is None:
            raise RuntimeError(f"Service '{self._name}' is not running.")
        if self._isStopping:
            raise RuntimeError(f"Service '{self._name}' is stopping.")

    def start(self, *args, **kwargs) -> None:
        self._assertStartReady()
        self.raiseEvent("ON_STARTING")

        lLoop = get_running_loop()
        self._isRunning = True
        self._pauseEvent.set()
        self._task = lLoop.create_task(
            self._serviceLoop(*args, **kwargs),
            name=self._name,
        )

    def stop(self, forceAfter: float = C_DEFAULT_FORCE_AFTER) -> None:
        self._assertStopReady()
        self.raiseEvent("ON_STOPPING")

        self._isStopping = True
        self._isRunning = False
        self._pauseEvent.set()

        lTask = self._task
        if lTask is not None:
            lLoop = get_running_loop()
            lLoop.call_later(forceAfter, self._cancelIfRunning, lTask)

    def _cancelIfRunning(self, task: Task) -> None:
        if not task.done():
            task.cancel()

    def pause(self) -> None:
        if not self._isRunning:
            raise RuntimeError(f"Service '{self._name}' is not running.")
        self._pauseEvent.clear()
        self.raiseEvent("ON_PAUSED")

    def resume(self) -> None:
        if not self._isRunning:
            raise RuntimeError(f"Service '{self._name}' is not running.")
        self._pauseEvent.set()
        self.raiseEvent("ON_RESUMED")

    async def _serviceLoop(self, *args, **kwargs) -> None:
        lWork = self.work
        if lWork is None: return

        await self.asyncRaiseEvent("ON_STARTED")

        try:
            while self._isRunning:
                await self._pauseEvent.wait()
                if not self._isRunning:
                    break

                await lWork(*args, **kwargs)

                if self._throttle:
                    await asyncSleep(self._throttle)

        except CancelledError:
            pass

        finally:
            self._isRunning = False
            self._isStopping = False
            self._pauseEvent.set()
            self._task = None
            await self.asyncRaiseEvent("ON_STOPPED")


# ==================================================================================
__all__ = ["AsyncService"]
