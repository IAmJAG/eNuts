# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import (
    AbstractEventLoop,
    CancelledError,
    Future,
    Task,
    get_running_loop,
    to_thread,
)
from asyncio import sleep as asyncSleep
from multiprocessing import Event, Process, Queue
from multiprocessing.synchronize import Event as syncEvent
from queue import Empty
from typing import Any, Awaitable, Callable, Dict, Optional

# ==================================================================================
from jAGFx.services import C_DEFAULT_STOP_TIMEOUT, AsyncProcess, processEntry

# ==================================================================================
from ..devices import SCRCPY
from .__helper import asyncCloseQueue, asyncDrainQueue, closeQueue, drainQueue
from .__SCRCPYOptions import SCRCPYOptions


# ==================================================================================
class OPEmitter(AsyncProcess, SCRCPY):
    def __init__(self, serial: str, name: str | None = None, options: SCRCPYOptions | None = None) -> None:
        SCRCPY.__init__(self, serial=serial, name=name)
        AsyncProcess.__init__(self, work=self._work, name=name)        

        self._inQueue: Optional[Queue] = None
        self._outQueues: Dict[str, Queue] = None

        self._stopTask: Optional[Task] = None
        self._options: Optional[SCRCPYOptions] = options

        self._receiverTask: Optional[Task] = None
        self._processes: Dict[str, Process] = dict[str, Process]()

    async def _receiver(self, shutdownEvent: syncEvent, queue: Queue, clientId: Optional[str] = None) -> None:
        # if clientId is None this is the server

        # Intentionally left as a stub for IntelliSense / type-checker signature
        def isShuttingdown() -> bool: ...
        isShuttingdown: Callable[[], bool] = shutdownEvent.is_set

        def isClient() -> bool: 
            return clientId is not None

        self._clientId = clientId
        try:
            while not isShuttingdown():
                msg = await to_thread(queue.get)  # queue.get
                print(msg)

        except Exception:
            raise

        finally:
            asyncDrainQueue(queue)

    async def _work(self, clientId: str, shutdownEvent: syncEvent, inQueue: Queue, outQueue: Queue) -> None:
        self._outQueue = outQueue
        try:            
            receiver: Task = createTask(
                self._receiver, shutdownEvent, inQueue, clientId
            )
            self._receiverTask = receiver

        except Exception:
            asyncCloseQueue(inQueue)
            raise RuntimeError(f"failed to run client process: {clientId}")
        
        try:
            await to_thread(shutdownEvent.wait)

        finally:
            if not receiver.done():
                receiver.cancel()

            try:
                await receiver

            except (CancelledError, Exception):
                pass

            finally:
                asyncCloseQueue(inQueue)

    def _start(self, clientId: str, shutdownEvent: syncEvent, outQueue: Queue) -> Queue:
        # Intentionally left as a stub for IntelliSense / type-checker signature
        async def work(shutdownEvent: syncEvent, *args, **kwargs): ...
        work: Callable[..., Awaitable] = self._work

        inQueue: Queue = Queue()

        process = Process(
            target=processEntry, args=(work, clientId, shutdownEvent, outQueue, inQueue),
            daemon=True, name=f"PROC_{clientId}",
        )
        self._processes[clientId] = process
        process.start()
        return inQueue

    def start(self, clientId: str) -> None:
        # Intentionally left as a stub for IntelliSense / type-checker signature
        def start(clientId: str, shutdonwEvent: syncEvent, outQueue: Queue) -> None: ...
        start: Callable[..., None] = self._start

        if self._shutdownEvent is None:
            self._shutdownEvent = syncEvent()
        
        if self._inQueue is None:
            self._inQueue = Queue()  # parent writes here (child reads)

        shutdownEvent: syncEvent = self._shutdownEvent
        outQueue = self._inQueue

        try:
            inQueue = start(clientId, shutdownEvent, outQueue)
            self._outQueues[clientId] = inQueue

        except Exception:
            closeQueue(inQueue)
            closeQueue(outQueue)
            raise

        if self._receiverTask is not None and not self._receiverTask.done():
            return

        def _onParentReceiverDone(task: Task) -> None:
            if self._receiverTask is task:
                self._receiverTask = None

            queKeys = list(self._outQueues.keys())
            for key in queKeys:
                queue: Queue = self._outQueues.pop(key)
                closeQueue(queue)
            closeQueue(outQueue)

        receiver: Task = createTask(self._receiver, shutdownEvent, outQueue)
        receiver.add_done_callback(_onParentReceiverDone)
        self._receiverTask = receiver

    async def stopAsync(self, timeout: float = C_DEFAULT_STOP_TIMEOUT, forced: bool = False) -> None:
        try:
            await super().asyncStop(timeout=timeout, forced=forced)

        finally:
            try:
                await self._endReceiver()

            finally:
                self._closeQueues()

    def stop(self, timeout: float = C_DEFAULT_STOP_TIMEOUT, forced: bool = False) -> None:
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

    async def _endReceiver(self) -> None:
        task = self._tasks

        if task is None: return

        if not task.done():
            task.cancel()

        try:
            await task

        except (CancelledError, Exception):
            pass

        finally:
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

    

    # Convenience for subclasses that want to send from the parent
    async def _dispatch(self, msg: Any) -> None:
        if self._outQueue is not None:
            self._outQueue.put(msg)
