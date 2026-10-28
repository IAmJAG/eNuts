# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import CancelledError, Event, Task, get_running_loop, wait_for
from asyncio import TimeoutError as AsyncTimeoutError
from inspect import iscoroutinefunction
from typing import Awaitable, Callable

# ==================================================================================
from jAGFx.names import getRandomName

# ==================================================================================
from ..types.interface.services import iService
from .__subscription import AsyncSubscription


# ==================================================================================
class AsyncService(iService, AsyncSubscription):
    """Async work loop with optional throttle and interruptible wait.

    Two distinct events control the loop:

    - ``_pauseEvent`` (pause / resume)
      Cleared by ``pause()``, set by ``resume()`` / ``start()`` / ``stop()``.
      While cleared the service cooperatively suspends *before* running work.
      This is a long-lived control signal for external pause/resume.

    - ``_wakeEvent`` (throttle / deadline)
      Used only for the post-work wait. Cleared immediately before waiting,
      set by ``wake()`` or by the throttle property setter. Allows the current
      throttle sleep to end early so a newly computed deadline is observed.
      This is a short-lived signal for dynamic scheduling, not for pause.
    """

    C_DEFAULT_FORCE_AFTER: float = 0.1

    def __init__(
        self,
        work: Callable[..., Awaitable] | None = None,
        name: str | None = None,
        throttle: float = 0.0,
    ) -> None:
        AsyncSubscription.__init__(self)

        if throttle < 0.0:
            raise ValueError("throttle must be greater than or equal to zero")

        if work is not None and not iscoroutinefunction(work):
            raise TypeError(
                "AsyncService requires an awaitable (coroutine function) work argument"
            )

        self.work: Callable[..., Awaitable] | None = work
        self._name: str = name or getRandomName()
        self._isRunning: bool = False
        self._isStopping: bool = False
        self._pauseEvent: Event = Event()
        self._pauseEvent.set()
        self._wakeEvent: Event = Event()
        self._wakeEvent.set()
        self._task: Task[None] | None = None
        self._throttle: float = throttle

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
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

    @property
    def throttle(self) -> float:
        """Seconds to wait after each work iteration. 0.0 means no wait."""
        return self._throttle

    @throttle.setter
    def throttle(self, value: float) -> None:
        if value < 0.0:
            raise ValueError("throttle must be greater than or equal to zero")
        self._throttle = value
        # Ensure a pending wait observes the new duration promptly.
        self.wake()

    # Intentionally left as a stub for IntelliSense / type-checker signature
    async def work(self, *args, **kwargs): ...

    # ------------------------------------------------------------------
    # Control
    # ------------------------------------------------------------------
    def wake(self) -> None:
        """End the current throttle wait early so the loop re-evaluates.

        Safe to call at any time. Has no effect on the pause/resume state.
        """
        self._wakeEvent.set()

    def _assertStartReady(self) -> None:
        if self._isRunning:
            raise RuntimeError(f"Service '{self._name}' is already running.")

        if self._isStopping:
            raise RuntimeError(f"Service '{self._name}' is stopping.")

        if self.work is None or not iscoroutinefunction(self.work):
            raise TypeError(
                "AsyncService requires an awaitable (coroutine function) work argument"
            )

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
        self._wakeEvent.set()

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
        self._wakeEvent.set()

        lTask = self._task
        if lTask is None:
            self._isStopping = False
            return

        try:
            lLoop = get_running_loop()

        except RuntimeError:
            # Loop already stopped (e.g. finally after run_until_complete) — cancel now
            self._cancelIfRunning(lTask)
            self._task = None
            self._isStopping = False
            return

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
        if isNoOpMethod(self.work):
            return

        # Intentionally left as stubs for IntelliSense / type-checker signature
        async def pause(): ...
        async def work(*args, **kwargs): ...
        def throttleClear(): ...
        async def wakeWait(): ...

        async def throttle(timeout: float) -> None:
            await wait_for(wakeWait(), timeout=timeout)

        # cache the methods for performance
        pause = self._pauseEvent.wait
        work = self.work
        throttleClear = self._wakeEvent.clear
        wakeWait = self._wakeEvent.wait


        await self.asyncRaiseEvent("ON_STARTED")

        try:
            while self._isRunning: 
                await pause()
                if not self._isRunning: break

                await work(*args, **kwargs)

                timeout = self._throttle
                if timeout > 0.0:
                    throttleClear()
                    try:
                        await throttle(timeout)
                    except AsyncTimeoutError:
                        pass

        except CancelledError:
            pass

        finally:
            self._isRunning = False
            self._isStopping = False
            self._pauseEvent.set()
            self._wakeEvent.set()
            self._task = None
            await self.asyncRaiseEvent("ON_STOPPED")


# ==================================================================================
__all__ = ["AsyncService"]
