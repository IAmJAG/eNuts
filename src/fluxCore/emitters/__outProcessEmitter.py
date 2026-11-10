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
    3. Queues are closed and the process is joined.
    """

    def __init__(self, serial: str, name: str | None = None, options: SCRCPYOptions | None = None) -> None:
        SCRCPY.__init__(self, serial=serial, name=name)
        AsyncProcess.__init__(self, work=self.work, name=name)

        # These attributes are process-local after pickling; same names are safe.
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
            if not receiver.done(): receiver.cancel()

            try:
                await receiver

            except (CancelledError, Exception):
                pass

            self._closeQueue(outQueue)

    # --------------------------------------------------------------------------------
    # Shared receiver used by both parent and child
    # --------------------------------------------------------------------------------
    async def _receiver(self, shutdownEvent: syncEvent, queue: Queue) -> None:
        """Polls a queue until the shutdown Event is set, then drains."""
        while not shutdownEvent.is_set():
            try:
                msg = queue.get_nowait()

            except Empty:
                await asyncSleep(0.01)
                continue

            # Base implementation just prints; subclasses override or subscribe
            print(msg)

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
        # Create the two queues. Naming is from the parent's perspective.
        inQueue: Queue = Queue()   # child writes here
        outQueue: Queue = Queue()  # parent writes here (child reads)

        # Swap when handing to the child so each side's "in" is the other's "out"
        super().start(inQueue=outQueue, outQueue=inQueue, *args, **kwargs)

        self._inQueue = inQueue
        self._outQueue = outQueue

        try:
            loop = get_running_loop()

        except RuntimeError as ex:
            raise RuntimeError("requires a running event loop") from ex

        self._tasks = loop.create_task(
            self._receiver(self._shutdownEvent, inQueue)
        )

    def stop(self, timeout: float = AsyncProcess.C_DEFAULT_STOP_TIMEOUT, forced: bool = False) -> None:
        """Set Event, join process, cancel parent receiver, close queues."""
        if self._shutdownEvent is not None:
            self._shutdownEvent.set()

        super().stop(timeout=timeout, forced=forced)

        self._cancelTasks()

        self._closeQueue(self._inQueue)
        self._closeQueue(self._outQueue)
        self._inQueue = None
        self._outQueue = None

    def _cancelTasks(self) -> None:
        task = self._tasks
        if task is None or task.done():
            self._tasks = None
            return

        task.cancel()
        self._tasks = None

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
