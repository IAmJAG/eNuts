# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import CancelledError, Future, get_running_loop, to_thread
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
from ..types.interface.emitters import iSCRCPYEmitter
from .__SCRCPYOptions import SCRCPYOptions


# ==================================================================================
class OPEmitter(SCRCPY, AsyncProcess, iSCRCPYEmitter):
    """
    Out-of-process emitter base.

    Heavy work runs in a child process (AsyncProcess). Parent and child communicate
    via two multiprocessing Queues. Shutdown is cooperative via the shared Event:

    1. Shared Event is set.
    2. Both sides exit their receiver loops and drain remaining messages.
    3. Queues are closed only after the child process has exited (or already exited).
    """

    def __init__(self, serial: str, name: str | None = None, options: SCRCPYOptions | None = None) -> None:
        SCRCPY.__init__(self, serial=serial, name=name)
        AsyncProcess.__init__(self, work=self.work, name=name)

        # Process-local after pickling; same names are safe.
        self._inQueue: Optional[Queue] = None
        self._outQueue: Optional[Queue] = None
        self._tasks: Optional[Future] = None
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
        """Async shutdown: signal, reap process if needed, always clean parent resources."""
        try:
            await self._reapProcessAsync(timeout=timeout, forced=forced)

        finally:
            await self._finishParentReceiver()
            self._closeQueues()

    def stop(self, timeout: float = AsyncProcess.C_DEFAULT_STOP_TIMEOUT, forced: bool = False) -> None:
        """Sync entry. When a loop is running, delegates to stopAsync."""
        try:
            loop = get_running_loop()

        except RuntimeError:
            # No loop — reap synchronously, then clean
            try:
                self._reapProcessSync(timeout=timeout, forced=forced)

            finally:
                self._cancelTasks()
                self._closeQueues()
            return

        # Loop present — schedule the full coordinated sequence and return
        loop.create_task(self.stopAsync(timeout=timeout, forced=forced))

    async def _reapProcessAsync(self, timeout: float, forced: bool) -> None:
        """Set Event and wait for process exit. Tolerates already-exited process."""
        process = self._process
        if process is None:
            # Never started — nothing to reap
            return

        if self._shutdownEvent is not None:
            self._shutdownEvent.set()

        if not process.is_alive():
            # Already exited cooperatively; still close the handle
            process.close()
            self._process = None
            self._shutdownEvent = None
            return

        # Still alive — let the base class join / kill
        await super().stopAsync(timeout=timeout, forced=forced)

    def _reapProcessSync(self, timeout: float, forced: bool) -> None:
        """Synchronous counterpart of _reapProcessAsync."""
        process = self._process
        if process is None:
            return

        if self._shutdownEvent is not None:
            self._shutdownEvent.set()

        if not process.is_alive():
            process.close()
            self._process = None
            self._shutdownEvent = None
            return

        super().stop(timeout=timeout, forced=forced)

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
