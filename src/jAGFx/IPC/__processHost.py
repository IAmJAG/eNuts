# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import AbstractEventLoop, CancelledError, Task, get_running_loop, to_thread
from inspect import iscoroutinefunction
from multiprocessing import Event, Process, Queue
from multiprocessing.synchronize import Event as syncEvent
from queue import Empty
from threading import RLock
from typing import Any, Awaitable, Callable, Dict, List, Optional
from uuid import uuid4

# ==================================================================================
from jAGFx.services import C_DEFAULT_STOP_TIMEOUT, AsyncProcess, processEntry
from utilities import createTask

# ==================================================================================
from ..types.interface.communication.messages import iHandshake, iMessage
from .__helper import asyncCloseQueue, asyncDrainQueue, closeQueue, drainQueue
from .process import ProcessSnapshot


# ==================================================================================
class ProcessHost(AsyncProcess):
    def __init__(self, name: Optional[str] = None) -> None:
        AsyncProcess.__init__(self, work=None, name=name)

        # Parent -> one client. That client's inbound.
        self._outQueues: Dict[str, Queue] = {}

        # Clients -> parent. One shared inbound.
        self._inQueue: Optional[Queue] = None
        self._receiverTask: Optional[Task] = None

        self._stopTask: Optional[Task] = None

        self._lock: RLock = RLock()
        self._processes: Dict[int, ProcessSnapshot] = dict[int, Process]()

        self._loop: Optional[AbstractEventLoop] = None

    @property
    def processes(self) -> Dict[int, Process]: 
        with self._lock:  # This is OK, no race for the processes
            return self._processes

    async def _receiver(self, shutdownEvent: syncEvent, queue: Queue) -> None:
        try:
            def isShuttingdown() -> bool: ...
            isShuttingdown = shutdownEvent.is_set

            while not isShuttingdown():
                try:                    
                    msg: iMessage = await to_thread(queue.get, True, 0.1)

                except Empty:
                    continue

                self.raiseEvent("MESSAGE_RECEIVED", message=msg, nonBlocking=True)

        except Exception:
            await self.stopAsync(forced=True)
            raise

        finally:
            # Ensure shutdown event is set/triggered
            if not isShuttingdown(): shutdownEvent.set()
            await asyncDrainQueue(queue)
            await asyncCloseQueue(queue)

    def _handleMessage(self, message: iMessage) -> None:
        if isinstance(message, iHandshake):
            print("Received handshake processID:", message.processId)

        trace(f"Message received [{type(message).__name__}] [{message.payload}]")

    def _startProcess(self, shutdownEvent: syncEvent, clientQueue: Queue, sharedQueue: Queue) -> Process:
        async def worker(self, shutdownEvent, *args, **kwargs): ...
        worker: Callable[..., Awaitable] = self._work
        
        process = Process(
            target=processEntry,
            args=(worker, (shutdownEvent, clientQueue, sharedQueue), {}),
            daemon=True, name=f"PROC_{uuid4().hex}",
        )        
        process.start()        
        return process

    def _startReceiver(self, shutdownEvent: syncEvent, queue: Queue) -> None:
        receiverTask: Task = self._receiverTask
        if receiverTask is None or receiverTask.done():
            try:            
                receiverTask: Task = createTask(self._receiver, shutdownEvent, queue)
                self._receiverTask = receiverTask
                self.subscribe("MESSAGE_RECEIVED", self._handleMessage)

            except Exception as ex:
                trace("Failed to start", ex)
                cleanUpTask: Dict[str, bool] = {
                    "receiverTask": False, "drainQueue": False,
                    "closeQueue": False, "shutdownEvent": False,
                }

                try:
                    if receiverTask is not None and not receiverTask.done():
                        trace("Receiver task not yet done, canceling...")
                        receiverTask.cancel()
                        cleanUpTask["receiverTask"] = True

                    try: 
                        trace("Draining queue...")
                        drainQueue(queue)
                        cleanUpTask["drainQueue"] = True

                    except Empty:
                        pass

                    try: 
                        trace("closing queue...")
                        closeQueue(queue)
                        cleanUpTask["closeQueue"] = True

                    except Exception:
                        pass

                    if shutdownEvent is not None and not shutdownEvent.is_set():
                        trace("invoking shutdown...")
                        shutdownEvent.set()
                        cleanUpTask["shutdownEvent"] = True
                    
                finally:
                    self._inQueue = None                
                    self._shutdownEvent = None
                    self._receiverTask = None
                    trace(f"Cleaned up: {cleanUpTask}")

                raise
            
            return 

        trace("Receiver task already started")

    def start(self, worker: Callable[..., Awaitable]) -> None:
        if not iscoroutinefunction(worker):
            raise ValueError("worker must be a coroutine")
        
        shutdownEvent: Optional[syncEvent] = self._shutdownEvent
        sharedQueue: Optional[Queue] = self._inQueue

        if shutdownEvent is None:            
            shutdownEvent = Event()
            self._shutdownEvent = shutdownEvent
            trace("Created shutdown event")

        if sharedQueue is None:
            sharedQueue = Queue()
            self._inQueue = sharedQueue
            trace("Created shared queue")

        try:
            # creates main receiver task, returns immedieately if already started
            self._startReceiver(shutdownEvent, sharedQueue)

        except Exception:            
            raise

        clientQueue = Queue()
        trace("Created client queue")

        procSS: Optional[ProcessSnapshot] = None
        try:
            self._work = worker
            process: Process = self._startProcess(shutdownEvent, clientQueue, sharedQueue)
            with self._lock:
                procSS = ProcessSnapshot(process)
                
            
        except Exception as ex:
            self._resourceCleanup(procSS.identity, sharedQueue, clientQueue)
            raise

    def _resourceCleanup(self, clientId: str, sharedQueue: Queue, clientQueue: Queue) -> None:
        try:
            drainQueue(clientQueue)
        
        except Exception:
            pass

        try:            
            closeQueue(clientQueue)

        except Exception:
            pass

        procSS: ProcessSnapshot = self._processes.pop(clientId, None)        
        if procSS is not None:
            process: Process = procSS.process
            if process.is_alive():
                process.terminate()
                process.join()
            process.close()

        if not self._processes:
            if self._shutdownEvent is not None and not self._shutdownEvent.is_set():
                self._shutdownEvent.set()

            task = self._receiverTask
            self._receiverTask = None

            if task is not None and not task.done():
                task.cancel()

            try:
                drainQueue(sharedQueue)

            finally:
                closeQueue(sharedQueue)

            self._inQueue = None
            self._shutdownEvent = None

    def stop(self, timeout: float = C_DEFAULT_STOP_TIMEOUT, forced: bool = False) -> None:
        if self._stopTask is not None and not self._stopTask.done(): return

        try:
            loop = get_running_loop()

        except RuntimeError:
            self._stopSync(timeout=timeout, forced=forced)
            return

        self._stopTask = loop.create_task(
            self.stopAsync(timeout=timeout, forced=forced)
        )
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

    async def stopAsync(self, timeout: float = C_DEFAULT_STOP_TIMEOUT, forced: bool = False) -> None:
        if not self._processes and self._receiverTask is None: return

        self.raiseEvent("ON_STOPPING")
        shutdownEvent: Optional[syncEvent] = self._shutdownEvent

        try:
            if shutdownEvent is not None and not shutdownEvent.is_set():
                shutdownEvent.set()

            await self._finishReceiver()
            await to_thread(self._stopProcesses, timeout, forced)

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
        process: Process
        for process in self._processes.values():
            if process.is_alive():
                if forced: process.terminate()

                process.join(timeout)

                if process.is_alive():
                    process.terminate()
                    process.join(timeout)

                if process.is_alive():
                    process.kill()
                    process.join(1.0)

            process.close()

        self._processes.clear()

    def _onStopTaskDone(self, task: Task) -> None:
        try:
            task.result()

        except Exception as ex:
            task.get_loop().call_exception_handler(
                {
                    "message": f"ProcessHost '{self.name}' stopAsync failed",
                    "exception": ex, "task": task,
                }
            )

        finally:
            if self._stopTask is task:
                self._stopTask = None

    async def waitStopped(self) -> None:
        task = self._stopTask
        if task is not None:
            await task

    def _closeQueues(self) -> None:
        queues: List[Queue] = list(self._outQueues.values())
        for lQueue in queues:
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
            process = self._processes.get(clientId)
            return process is not None and process.is_alive()

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
__all__ = ["ProcessHost"]
