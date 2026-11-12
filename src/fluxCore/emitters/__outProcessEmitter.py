from __future__ import annotations

# ==================================================================================
from asyncio import CancelledError, Task, get_running_loop, to_thread
from multiprocessing import Process, Queue
from multiprocessing.synchronize import Event as syncEvent
from queue import Empty
from typing import Any, Dict, Optional

# ==================================================================================
from jAGFx.services import C_DEFAULT_STOP_TIMEOUT, AsyncProcess, processEntry
from utilities import createTask

# ==================================================================================
from ..devices import SCRCPY
from .__helper import asyncCloseQueue, closeQueue
from .__SCRCPYOptions import SCRCPYOptions


# ==================================================================================
async def _clientWorker(
    clientId: str,
    shutdownEvent: syncEvent,
    inQueue: Queue,
    outQueue: Queue,
) -> None:
    try:
        while not shutdownEvent.is_set():
            try:
                lMsg = await to_thread(inQueue.get, True, 0.1)

            except Empty:
                continue

            print(f"[{clientId}] {lMsg}")

    finally:
        # These are the worker process's local queue handles.
        await asyncCloseQueue(inQueue)
        await asyncCloseQueue(outQueue)


# ==================================================================================
class OPEmitter(AsyncProcess, SCRCPY):
    def __init__(
        self,
        serial: str,
        name: str | None = None,
        options: SCRCPYOptions | None = None,
    ) -> None:
        SCRCPY.__init__(self, serial=serial, name=name)
        # A module-level worker is spawn-safe; passing a bound method would
        # pickle the entire emitter (including its other Process instances).
        AsyncProcess.__init__(self, work=_clientWorker, name=name)

        # Parent -> clients: all client processes compete to consume this queue.
        self._outQueue: Optional[Queue] = None

        # Client -> parent: each client has a dedicated return queue.
        self._outQueues: Dict[str, Queue] = {}
        self._receiverTasks: Dict[str, Task] = {}

        self._stopTask: Optional[Task] = None
        self._options: Optional[SCRCPYOptions] = options
        self._processes: Dict[str, Process] = {}

    async def _receiver(
        self,
        shutdownEvent: syncEvent,
        queue: Queue,
        clientId: Optional[str] = None,
    ) -> None:
        while not shutdownEvent.is_set():
            try:
                lMsg = await to_thread(queue.get, True, 0.1)

            except Empty:
                continue

            if clientId is None:
                print(lMsg)
            else:
                print(f"[{clientId}] {lMsg}")

    def _start(
        self,
        clientId: str,
        shutdownEvent: syncEvent,
        sharedQueue: Queue,
        clientQueue: Queue,
    ) -> Process:
        lProcess = Process(
            target=processEntry,
            args=(
                _clientWorker,
                (clientId, shutdownEvent, sharedQueue, clientQueue),
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

        if self._shutdownEvent is None:
            self._shutdownEvent = syncEvent()

        if self._outQueue is None:
            self._outQueue = Queue()

        lShutdownEvent = self._shutdownEvent
        lSharedQueue = self._outQueue
        lClientQueue = Queue()

        try:
            self._start(
                clientId,
                lShutdownEvent,
                lSharedQueue,
                lClientQueue,
            )
            self._outQueues[clientId] = lClientQueue
            self._receiverTasks[clientId] = createTask(
                self._receiver,
                lShutdownEvent,
                lClientQueue,
                clientId,
            )

        except Exception:
            closeQueue(lClientQueue)
            lProcess = self._processes.pop(clientId, None)
            if lProcess is not None:
                if lProcess.is_alive():
                    lProcess.terminate()
                    lProcess.join()
                lProcess.close()

            if not self._processes:
                lShutdownEvent.set()
                closeQueue(lSharedQueue)
                self._outQueue = None
                self._shutdownEvent = None

            raise

    async def stopAsync(
        self,
        timeout: float = C_DEFAULT_STOP_TIMEOUT,
        forced: bool = False,
    ) -> None:
        if not self._processes and not self._receiverTasks:
            return

        self.raiseEvent("ON_STOPPING")

        try:
            if self._shutdownEvent is not None:
                self._shutdownEvent.set()

            # Receivers use a bounded queue.get timeout, so they can observe
            # shutdown without leaving a worker thread blocked indefinitely.
            for lTask in list(self._receiverTasks.values()):
                try:
                    await lTask

                except (CancelledError, Exception):
                    pass

            await to_thread(self._stopProcesses, timeout, forced)

        finally:
            self._closeQueues()
            self._shutdownEvent = None
            self.raiseEvent("ON_STOPPED")

    def stop(
        self,
        timeout: float = C_DEFAULT_STOP_TIMEOUT,
        forced: bool = False,
    ) -> None:
        if self._stopTask is not None and not self._stopTask.done():
            return

        try:
            lLoop = get_running_loop()

        except RuntimeError:
            self._stopSync(timeout=timeout, forced=forced)
            return

        self._stopTask = lLoop.create_task(
            self.stopAsync(timeout=timeout, forced=forced)
        )
        self._stopTask.add_done_callback(self._onStopTaskDone)

    def _stopSync(
        self,
        timeout: float = C_DEFAULT_STOP_TIMEOUT,
        forced: bool = False,
    ) -> None:
        if not self._processes and not self._receiverTasks:
            return

        self.raiseEvent("ON_STOPPING")

        try:
            if self._shutdownEvent is not None:
                self._shutdownEvent.set()

            for lTask in self._receiverTasks.values():
                if not lTask.done():
                    lTask.cancel()

            self._stopProcesses(timeout, forced)

        finally:
            self._closeQueues()
            self._shutdownEvent = None
            self.raiseEvent("ON_STOPPED")

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
                "message": f"OPEmitter '{self.name}' stopAsync failed",
                "exception": ex,
                "task": task,
                self._stopTask = None

    async def waitStopped(self) -> None:
        lTask = self._stopTask
        if lTask is not None:
            await lTask

    def _closeQueues(self) -> None:
        for lQueue in self._outQueues.values():
            closeQueue(lQueue)

        self._outQueues.clear()
        self._receiverTasks.clear()

        closeQueue(self._outQueue)
        self._outQueue = None

    def running(self) -> bool:
        return any(lProcess.is_alive() for lProcess in self._processes.values())

    # Convenience for subclasses that want to send from the parent.
    async def _dispatch(self, msg: Any) -> None:
        if self._outQueue is not None:
            await to_thread(self._outQueue.put, msg)


# ==================================================================================
__all__ = ["OPEmitter"]
