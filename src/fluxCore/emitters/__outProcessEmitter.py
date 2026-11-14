from __future__ import annotations

# ==================================================================================
from asyncio import CancelledError, Task, get_running_loop, to_thread
from multiprocessing import Event, Process, Queue
from multiprocessing.synchronize import Event as syncEvent
from queue import Empty
from typing import Any, Awaitable, Callable, Dict, Optional

# ==================================================================================
from jAGFx.services import C_DEFAULT_STOP_TIMEOUT, AsyncProcess, processEntry
from utilities import createTask

# ==================================================================================
from ..configurations.scrcpy import SCRCPYConfig
from ..devices import SCRCPY
from .__emitterWorkers import SCRCPYWorker
from .__helper import closeQueue


# ==================================================================================
class outOfProcessEmitter(AsyncProcess, SCRCPY):
    def __init__(
        self, serial: str, name: str | None = None, options: SCRCPYConfig | None = None,
        worker: Callable[..., Awaitable] | None = None,
    ) -> None:
        SCRCPY.__init__(self, serial=serial, name=name)
        AsyncProcess.__init__(self, work=worker or SCRCPYWorker, name=name)

        # Parent -> one client. That client's inbound.
        self._outQueues: Dict[str, Queue] = {}

        # Clients -> parent. One shared inbound.
        self._inQueue: Optional[Queue] = None
        self._receiverTask: Optional[Task] = None

        self._stopTask: Optional[Task] = None
        self._options: Optional[SCRCPYConfig] = options
        self._processes: Dict[str, Process] = {}

    async def _receiver(self, shutdownEvent: syncEvent, queue: Queue) -> None:
        try:
            def isShuttingdown() -> bool: ...
            isShuttingdown = shutdownEvent.is_set

            while not isShuttingdown():
                try:
                    msg = await to_thread(queue.get, True, 0.1)

                except Empty:
                    continue

                print(msg)

        finally:
            return

    async def stopAsync( self, timeout: float = C_DEFAULT_STOP_TIMEOUT, forced: bool = False) -> None:
        if not self._processes and self._receiverTask is None:
            return

        self.raiseEvent("ON_STOPPING")

        try:
            if self._shutdownEvent is not None:
                self._shutdownEvent.set()

            await self._finishReceiver()
            await to_thread(self._stopProcesses, timeout, forced)

        finally:
            self._closeQueues()
            self._shutdownEvent = None
            self.raiseEvent("ON_STOPPED")
    
    def _startProcess(
        self, clientId: str, shutdownEvent: syncEvent,
        clientQueue: Queue, sharedQueue: Queue,
    ) -> Process:
        lProcess = Process(
            target=processEntry,
            args=(
                self._worker,
                (clientId, shutdownEvent, clientQueue, sharedQueue),
                {},
            ),
            daemon=True,
            name=f"PROC_{clientId}",
        )
        lProcess.start()
        self._processes[clientId] = lProcess
        return lProcess

    def start(self, clientId: str) -> None:
        get_running_loop()

        if clientId in self._processes:
            raise RuntimeError(f"Client '{clientId}' has already been started.")

        shutdownEvent: Optional[syncEvent] = self._shutdownEvent
        sharedQueue: Optional[Queue] = self._inQueue

        if shutdownEvent is None:
            shutdownEvent = Event()            
            self._shutdownEvent = shutdownEvent

        if sharedQueue is None:
            sharedQueue = Queue()
            self._inQueue = sharedQueue

        clientQueue = Queue()

        try:
            self._startProcess(clientId, shutdownEvent, clientQueue, sharedQueue)
            self._outQueues[clientId] = clientQueue

            if self._receiverTask is None:
                self._receiverTask = createTask(self._receiver, shutdownEvent, sharedQueue)

        except Exception:
            closeQueue(clientQueue)

            lProcess = self._processes.pop(clientId, None)
            if lProcess is not None:
                if lProcess.is_alive():
                    lProcess.terminate()
                    lProcess.join()
                lProcess.close()

            if not self._processes:
                if self._receiverTask is not None and not self._receiverTask.done():
                    self._receiverTask.cancel()

                self._receiverTask = None

                closeQueue(sharedQueue)                    
                self._inQueue = None
                self._shutdownEvent = None

            raise
    
    def stop(self, timeout: float = C_DEFAULT_STOP_TIMEOUT, forced: bool = False) -> None:
        if self._stopTask is not None and not self._stopTask.done():
            return

        try:
            lLoop = get_running_loop()

        except RuntimeError:
            self._stopSync(timeout=timeout, forced=forced)
            return

        self._stopTask = lLoop.create_task(self.stopAsync(timeout=timeout, forced=forced))
        self._stopTask.add_done_callback(self._onStopTaskDone)

    def _stopSync(self, timeout: float = C_DEFAULT_STOP_TIMEOUT, forced: bool = False) -> None:
        if not self._processes and self._receiverTask is None: return

        self.raiseEvent("ON_STOPPING")

        try:
            if self._shutdownEvent is not None:
                self._shutdownEvent.set()

            if self._receiverTask is not None and not self._receiverTask.done():
                self._receiverTask.cancel()

            self._stopProcesses(timeout, forced)

        finally:
            self._closeQueues()
            self._shutdownEvent = None
            self.raiseEvent("ON_STOPPED")

    async def _finishReceiver(self) -> None:
        task = self._receiverTask
        if task is None: return

        try:
            await task

        except (CancelledError, Exception):
            pass

        self._receiverTask = None

    def _stopProcesses(self, timeout: float, forced: bool) -> None:
        for lProcess in self._processes.values():
            if lProcess.is_alive():
                if forced:
                    lProcess.terminate()

                lProcess.join(timeout)

                if lProcess.is_alive():
                    lProcess.terminate()
                    lProcess.join(timeout)

                if lProcess.is_alive():
                    lProcess.kill()
                    lProcess.join(1.0)

            lProcess.close()

        self._processes.clear()

    def _onStopTaskDone(self, task: Task) -> None:
        try:
            task.result()

        except Exception as ex:
            task.get_loop().call_exception_handler({
                "message": f"outOfProcessEmitter '{self.name}' stopAsync failed",
                "exception": ex,
                "task": task,
            })

        finally:
            if self._stopTask is task:
                self._stopTask = None

    async def waitStopped(self) -> None:
        lTask = self._stopTask
        if lTask is not None:
            await lTask

    def _closeQueues(self) -> None:
        for lQueue in list(self._outQueues.values()):
            try:
                closeQueue(lQueue)

            except Exception:
                pass

        self._outQueues.clear()

        try:
            closeQueue(self._inQueue)

        except Exception:
            pass

        self._inQueue = None
        self._receiverTask = None

    def running(self, clientId: str | None = None) -> bool:
        if clientId is not None:
            lProcess = self._processes.get(clientId)
            return lProcess is not None and lProcess.is_alive()

        return (
            self._shutdownEvent is not None
            and not self._shutdownEvent.is_set()
            and len(self._processes) > 0
        )

    async def _dispatch(self, clientId: str, msg: Any) -> None:
        lQueue = self._outQueues.get(clientId)
        if lQueue is not None:
            await to_thread(lQueue.put, msg)


# ==================================================================================
__all__ = ["outOfProcessEmitter"]
