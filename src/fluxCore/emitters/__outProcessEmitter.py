# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import CancelledError, Future, Task, get_running_loop, to_thread
from asyncio import sleep as asyncSleep
from multiprocessing import Queue
from multiprocessing.synchronize import Event as syncEvent
from queue import Empty

# ==================================================================================
from typing import Any, Optional

# ==================================================================================
from jAGFx.services import AsyncProcess

# ==================================================================================
from ..devices import SCRCPY
from .__SCRCPYOptions import SCRCPYOptions


# ==================================================================================
class OPEmitter(AsyncProcess, SCRCPY):
    """
    Out-of-process emitter base.

    Heavy work runs in a child process (AsyncProcess). Parent and child communicate
    via two multiprocessing Queues.

    Process lifecycle and ON_STOPPING / ON_STOPPED are owned by AsyncProcess.
    OPEmitter only adds parent-receiver and queue cleanup.

    Satisfies iSCRCPYEmitter structurally. It is not an explicit base:
    SCRCPY contributes iDevice, AsyncProcess contributes iSubscription before
    iService, and iEmitter wants iService / iSubscription / iDevice. Those
    orders cannot be linearized together (same pattern as SCRCPYEmitter).
    """

    def __init__(self, serial: str, name: str | None = None, options: SCRCPYOptions | None = None) -> None:
        AsyncProcess.__init__(self, work=self.work, name=name)
        SCRCPY.__init__(self, serial=serial, name=name)

        # Process-local after pickling; same names are safe.
        self._inQueue: Optional[Queue] = None
        self._outQueue: Optional[Queue] = None
        self._tasks: Optional[Future] = None
        self._stopTask: Optional[Task] = None
        self._options: SCRCPYOptions | None = options

    # --------------------------------------------------------------------------------
    # Child-process entry point
    # --------------------------------------------------------------------------------
    async def work(self, shutdownEvent: syncEvent, inQueue: Queue, outQueue: Queue, *args, **kwargs) -> None:
        self._outQueue = outQueue

        receiver = get_running_loop().create_task(
            self._receiver(shutdownEvent, inQueue)
        )

        try:
            await to_thread(shutdownEvent.wait)

        finally:
            # Hard cancel is still allowed; drain happens inside _receiver.finally
            if not receiver.done():
                receiver.cancel()

            try:
                await receiver

            except (CancelledError, Exception):
                pass

            self._closeQueue(outQueue)

    # --------------------------------------------------------------------------------
    # Shared receiver used by both parent and child
    # --------------------------------------------------------------------------------
    async def _receiver(self, shutdownEvent: syncEvent, queue: Queue) -> None:
        """Polls a queue until the shutdown Event is set or the task is cancelled.

        Drain always runs (normal exit or hard cancel).
        """
        try:
            while not shutdownEvent.is_set():
                try:
                    msg = queue.get_nowait()

                except Empty:
                    await asyncSleep(0.01)
                    continue

                # Base implementation just prints; subclasses override or subscribe
                print(msg)

        finally:
            self._drainQueue(queue)

    def _drainQueue(self, queue: Queue) -> None:
        while True:
            try:
                queue.get_nowait()

            except Empty:
                break

    # --------------------------------------------------------------------------------
    # Parent API
    # --------------------------------------------------------------------------------
    def start(self, *args, **kwargs) -> None:
        # Fail fast before any side effects
        try:
            loop = get_running_loop()

        except RuntimeError as ex:
            raise RuntimeError("OPEmitter.start() requires a running event loop") from ex

        inQueue: Queue = Queue()   # child writes here
        outQueue: Queue = Queue()  # parent writes here (child reads)

        # Assign early so a failed start can still close them
        self._inQueue = inQueue
        self._outQueue = outQueue

        try:
            # Swap when handing to the child so each side's "in" is the other's "out"
            super().start(inQueue=outQueue, outQueue=inQueue, *args, **kwargs)

        except Exception:
            self._closeQueues()
            raise

        self._tasks = loop.create_task(
            self._receiver(self._shutdownEvent, inQueue)
        )

    async def stopAsync(self, timeout: float = AsyncProcess.C_DEFAULT_STOP_TIMEOUT, forced: bool = False) -> None:
        """Async shutdown. Process lifecycle stays in AsyncProcess; emitter cleanup is additive."""
        try:
            await super().stopAsync(timeout=timeout, forced=forced)

        finally:
            try:
                await self._finishParentReceiver()

            finally:
                self._closeQueues()

    def stop(self, timeout: float = AsyncProcess.C_DEFAULT_STOP_TIMEOUT, forced: bool = False) -> None:
        """Sync entry. When a loop is running, schedules a retained stopAsync task."""
        # Coalesce: if a shutdown is already in flight, do not start another
        if self._stopTask is not None and not self._stopTask.done():
            return

        try:
            loop = get_running_loop()

        except RuntimeError:
            # No loop — use inherited sync stop, then emitter cleanup
            try:
                super().stop(timeout=timeout, forced=forced)

            finally:
                self._cancelTasks()
                self._closeQueues()
            return

        # Loop present — retain the task so failures are observable
        self._stopTask = loop.create_task(self.stopAsync(timeout=timeout, forced=forced))
        self._stopTask.add_done_callback(self._onStopTaskDone)

    def _onStopTaskDone(self, task: Task) -> None:
        """Surface shutdown failures instead of silently dropping them."""
        try:
            task.result()

        except Exception as ex:
            # Re-raise on the loop so it is not an unretrieved task exception
            get_running_loop().call_exception_handler({
                "message": f"OPEmitter '{self.name}' stopAsync failed",
                "exception": ex,
                "task": task,
            })

        finally:
            if self._stopTask is task:
                self._stopTask = None

    async def waitStopped(self) -> None:
        """Await the scheduled shutdown task if one exists."""
        task = self._stopTask
        if task is None:
            return

        await task

    async def _finishParentReceiver(self) -> None:
        task = self._tasks
        if task is None:
            return

        if not task.done():
            task.cancel()

        try:
            await task

        except (CancelledError, Exception):
            pass

        self._tasks = None

    def _cancelTasks(self) -> None:
        """Sync cancel used only on the no-loop stop path."""
        task = self._tasks
        if task is None or task.done():
            self._tasks = None
            return

        task.cancel()
        self._tasks = None

    def _closeQueues(self) -> None:
        self._closeQueue(self._inQueue)
        self._closeQueue(self._outQueue)
        self._inQueue = None
        self._outQueue = None

    @staticmethod
    def _closeQueue(queue: Optional[Queue]) -> None:
        if queue is None:
            return

        try:
            queue.close()
            queue.cancel_join_thread()

        except Exception:
            pass

    # Convenience for subclasses that want to send from the parent
    async def _dispatch(self, msg: Any) -> None:
        if self._outQueue is not None:
            self._outQueue.put(msg)
