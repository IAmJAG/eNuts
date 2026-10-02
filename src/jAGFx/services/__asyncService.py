# ==================================================================================
from asyncio import CancelledError, Event, Task, get_running_loop
from asyncio import sleep as asyncSleep
from time import sleep
from typing import Awaitable, Callable

# ==================================================================================
from jAGFx.names import getRandomName

# ==================================================================================
from ..types.interface.services import iService


# ==================================================================================
class AsyncService(iService):
    """Run one asynchronous unit of work as a managed asyncio task."""

    def __init__(self, unitOfWork: Callable[..., Awaitable] | None = None,
        name: str | None = None, throttle: float = 0.0,
    ) -> None:
        if throttle < 0.0:
            raise ValueError("throttle must be greater than or equal to zero")

        self._name = getRandomName() if name is None else name
        self._work = unitOfWork
        self._isRunning = False
        self._isStopping = False
        self._pauseEvent = Event()
        self._pauseEvent.set()
        self._task: Task[None] | None = None
        self._throttle = throttle

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

    def start(self, *args, **kwargs) -> None:
        if self._isRunning:
            warning(f"Service {self.name} is already running", RuntimeWarning)
            return

        if self._isStopping:
            warning(f"Service {self.name} is stopping", RuntimeWarning)
            return

        if self._work is None:
            raise RuntimeError("AsyncService requires a unitOfWork")

        runningLoop = get_running_loop()
        self._isRunning = True
        self._pauseEvent.set()
        self._starting()
        self._task = runningLoop.create_task(
            self._serviceLoop(*args, **kwargs),
            name=self._name,
        )

    def stop(self, forceAfter: float = 0.1) -> None:
        if not self._isRunning and self._task is None:
            warning(
                f"Service {self.name} is not running",
                RuntimeWarning,
            )
            return

        if self._isStopping:
            warning(f"Service {self.name} is stopping", RuntimeWarning)
            return

        self._isStopping = True
        self._isRunning = False
        self._pauseEvent.set()
        self._stopping()

        task: Task = self._task
        loop = get_running_loop()
        loop.call_later(forceAfter, self._cancelIfRunning, task)

    def _cancelIfRunning(self, task: Task) -> None:
        if not task.done():
            task.cancel()

    def pause(self) -> None:
        if self._isRunning:
            self._pauseEvent.clear()
            self._paused()
            return

        warning(f"Service {self.name} is not running", RuntimeWarning)

    def resume(self) -> None:
        if self._isRunning:
            self._pauseEvent.set()
            self._resumed()
            return

        warning(f"Service {self.name} is not running", RuntimeWarning)

    async def _serviceLoop(self, *args, **kwargs) -> None:
        work = self._work
        if work is None:
            return

        self._started()

        try:
            while self._isRunning:
                await self._pauseEvent.wait()
                if not self._isRunning:
                    break

                await work(*args, **kwargs)

                if self._throttle:
                    await asyncSleep(self._throttle)

        except CancelledError:
            pass

        finally:
            self._isRunning = False
            self._isStopping = False
            self._pauseEvent.set()
            self._task = None
            self._stopped()

    def setOnStopping(self, callback: callable) -> None:
        self._stopping = callback

    def setOnStarting(self, callback: callable) -> None:
        self._starting = callback

    def setOnStop(self, callback: callable) -> None:
        self._stopped = callback

    def setOnStart(self, callback: callable) -> None:
        self._started = callback

    def setOnPause(self, callback: callable) -> None:
        self._paused = callback

    def setOnResume(self, callback: callable) -> None:
        self._resumed = callback

    def _starting(self): ...
    def _started(self): ...
    def _stopping(self): ...
    def _stopped(self): ...
    def _paused(self): ...
    def _resumed(self): ...


# ==================================================================================
__all__ = ["AsyncService"]