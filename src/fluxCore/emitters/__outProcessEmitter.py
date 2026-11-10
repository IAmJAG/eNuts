# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import CancelledError, Future, Task, gather, get_running_loop, to_thread
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
# Sentinel used for ordered drain. Distinct object so it cannot collide with real payloads.
_SHUTDOWN_SENTINEL: Any = object()


# ==================================================================================
class OPEmitter(SCRCPY, AsyncProcess, iSCRCPYEmitter):
    """
    Out-of-process emitter base.

    Heavy work runs in a child process (AsyncProcess). Parent and child communicate
    via two multiprocessing Queues. Shutdown is cooperative:

    1. Shared Event is set.
    2. Shutdown sentinels are injected into both directions.
    3. Both sides drain remaining messages then exit.
    4. Queues are closed and the process is joined.
    """

    def __init__(self, serial: str, name: str | None = None, options: SCRCPYOptions | None = None) -> None:
        SCRCPY.__init__(self, serial=serial, name=name)
        AsyncProcess.__init__(self, work=self.work, name=name)

        # Parent-side state (child has its own instance after pickle)
        self._parentInQueue: Optional[Queue] = None
        self._parentOutQueue: Optional[Queue] = None
        self._parentTasks: Optional[Future] = None
        self._options: SCRCPYOptions | None = options

    # --------------------------------------------------------------------------------
    # Child-process entry point
    # --------------------------------------------------------------------------------
    async def work(self, shutdownEvent: syncEvent, inQueue: Queue, outQueue: Queue, *args, **kwargs) -> None:
        """Runs only inside the child process."""
        self._childOutQueue = outQueue

        receiver = asyncio_create_task_safe(self._receiver(shutdownEvent, inQueue, is_child=True))

        try:
            # Block until the shared Event is set (or the process is killed)
            await to_thread(shutdownEvent.wait)
        finally:
            # Guarantee the receiver is cancelled and awaited so no feeder thread is left
            if not receiver.done():
                receiver.cancel()
            try:
                await receiver
            except (CancelledError, Exception):
                pass

            self._close_queue(outQueue)

    # --------------------------------------------------------------------------------
    # Shared receiver used by both parent and child
    # --------------------------------------------------------------------------------
    async def _receiver(self, shutdownEvent: syncEvent, queue: Queue, is_child: bool = False) -> None:
        """Polls a queue until sentinel or shutdown Event."""
        while True:
            if shutdownEvent.is_set():
                break

            try:
                msg = queue.get_nowait()
            except Empty:
                await asyncSleep(0.01)
                continue

            if msg is _SHUTDOWN_SENTINEL:
                break

            # Base implementation just prints; subclasses override or subscribe
            print(msg)

        # Drain any remaining items that arrived before the sentinel
        self._drain_queue(queue)

    def _drain_queue(self, queue: Queue) -> None:
        """Non-blocking drain of leftover messages (including sentinels)."""
        while True:
            try:
                queue.get_nowait()
            except Empty:
                break

    # --------------------------------------------------------------------------------
    # Parent API
    # --------------------------------------------------------------------------------
    def start(self, *args, **kwargs) -> None:
        # Create the two queues. Naming is from the parent's perspective.
        parent_in: Queue = Queue()   # child writes here
        parent_out: Queue = Queue()  # parent writes here (child reads)

        # Swap when handing to the child so each side's "in" is the other's "out"
        super().start(inQueue=parent_out, outQueue=parent_in, *args, **kwargs)

        self._parentInQueue = parent_in
        self._parentOutQueue = parent_out

        # Schedule the parent receiver on the running loop (required)
        try:
            loop = get_running_loop()
        except RuntimeError as ex:
            raise RuntimeError("OPEmitter.start() requires a running event loop") from ex

        self._parentTasks = loop.create_task(
            self._receiver(self._shutdownEvent, parent_in, is_child=False)
        )

    def stop(self, timeout: float = AsyncProcess.C_DEFAULT_STOP_TIMEOUT, forced: bool = False) -> None:
        """Coordinated stop: Event + sentinels + queue close + process join."""
        # 1. Signal both sides
        if self._shutdownEvent is not None:
            self._shutdownEvent.set()

        # 2. Inject sentinels so both receivers exit even if they are blocked on sleep
        self._put_sentinel(self._parentOutQueue)   # child will see it
        self._put_sentinel(self._parentInQueue)    # parent receiver will see it

        # 3. Let the base class join / kill the process
        super().stop(timeout=timeout, forced=forced)

        # 4. Clean parent-side task
        self._cancel_parent_tasks()

        # 5. Close queues so feeder threads exit
        self._close_queue(self._parentInQueue)
        self._close_queue(self._parentOutQueue)
        self._parentInQueue = None
        self._parentOutQueue = None

    def _put_sentinel(self, queue: Optional[Queue]) -> None:
        if queue is None:
            return
        try:
            queue.put_nowait(_SHUTDOWN_SENTINEL)
        except Exception:
            # Queue already closed or full — best effort
            pass

    def _cancel_parent_tasks(self) -> None:
        task = self._parentTasks
        if task is None or task.done():
            self._parentTasks = None
            return

        task.cancel()
        # Do not call .result() here; the loop will handle it.
        # If we are inside a running loop the task will be reaped normally.
        self._parentTasks = None

    @staticmethod
    def _close_queue(queue: Optional[Queue]) -> None:
        if queue is None:
            return
        try:
            queue.close()
            queue.cancel_join_thread()
        except Exception:
            pass

    # Convenience for subclasses that want to send from the parent
    async def _dispatch(self, msg: Any) -> None:
        if self._parentOutQueue is not None:
            self._parentOutQueue.put(msg)


# ==================================================================================
def asyncio_create_task_safe(coro) -> Task:
    """Helper so the child can schedule without importing get_running_loop at module level in a way that confuses pickling."""
    return get_running_loop().create_task(coro)
