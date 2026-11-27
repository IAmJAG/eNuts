# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import AbstractEventLoop, CancelledError, Task, get_running_loop, to_thread
from collections.abc import Awaitable, Callable
from inspect import iscoroutinefunction
from multiprocessing import Event, Process, Queue, active_children
from multiprocessing.synchronize import Event as syncEvent
from queue import Empty
from threading import RLock
from typing import Any
from uuid import uuid4

# ==================================================================================
from jAGFx.services import C_DEFAULT_STOP_TIMEOUT, AsyncProcess, processEntry
from utilities import createTask

# ==================================================================================
from ..types.interface.communication import iProcessHost
from ..types.interface.communication.client import iClient
from ..types.interface.communication.messages import iMessage
from .__exceptions import ClientNotFoundException
from .__helper import asyncCloseQueue, asyncDrainQueue, closeQueue, drainQueue
from .client import Client, handlerType
from .message import Handshake


# ==================================================================================
class ProcessHost(AsyncProcess, iProcessHost):
    def __init__(self, name: str | None = None) -> None:
        AsyncProcess.__init__(self, work=None, name=name)

        # Parent -> one client. That client's inbound.
        self._outQueues: dict[str, Queue] = {}

        # Clients -> parent. One shared inbound.
        self._inQueue: Queue | None = None
        self._receiverTask: Task | None = None

        self._stopTask: Task | None = None

        self._lock: RLock = RLock()
        self._clients: dict[int, iClient] = dict[int, Client]()

        self._loop: AbstractEventLoop | None = None

    @property
    def clients(self) -> dict[int, Process]: 
        with self._lock:
            return self._clients

    async def waitStopped(self) -> None:
        task = self._stopTask
        if task is not None:
            await task

    async def stopAsync(self, timeout: float = C_DEFAULT_STOP_TIMEOUT, forced: bool = False) -> None:
        if not self._clients and self._receiverTask is None:
            return

        self.raiseEvent("ON_STOPPING")
        shutdownEvent: syncEvent | None = self._shutdownEvent

        try:
            if shutdownEvent is not None and not shutdownEvent.is_set():
                shutdownEvent.set()

            await self._finishReceiver()
            await to_thread(self._stopProcesses, timeout, forced)

        finally:
            self._closeQueues()
            self._shutdownEvent = None
            self.raiseEvent("ON_STOPPED")

    async def _receiver(self, shutdownEvent: syncEvent, queue: Queue) -> None:
        try:
            def isShuttingdown() -> bool: ...
            isShuttingdown = shutdownEvent.is_set

            while not isShuttingdown():
                try:                    
                    msg: iMessage = await to_thread(queue.get, True, 0.1)

                except Empty: continue

                self.raiseEvent("MESSAGE_RECEIVED", message=msg)

        except Exception:
            await self.stopAsync(forced=True)
            raise

        finally:
            # Ensure shutdown event is set/triggered
            if not isShuttingdown(): shutdownEvent.set()
            await asyncDrainQueue(queue)
            await asyncCloseQueue(queue)

    async def _finishReceiver(self) -> None:
        task = self._receiverTask
        if task is None: return

        try:
            await task

        except (CancelledError, Exception):
            pass

        self._receiverTask = None

    async def _dispatch(self, clientId: str, msg: Any) -> None:
        queue = self._outQueues.get(clientId)
        if queue is None:
            warning("Client queues not found")
            return 
        
        queue.put(msg)
    
    def start(
        self, worker: Callable[..., Awaitable],
        clientType: iClient,
        handler: handlerType
    ) -> iClient:
        if not iscoroutinefunction(worker): 
            raise ValueError("worker must be a coroutine")
        
        shutdownEvent: syncEvent | None = self._shutdownEvent
        sharedQueue: Queue | None = self._inQueue

        if shutdownEvent is None:
            shutdownEvent = Event()
            self._shutdownEvent = shutdownEvent
            trace("Created shutdown event")

        if sharedQueue is None:
            sharedQueue = Queue()
            self._inQueue = sharedQueue
            trace("Created shared queue")

        
        # creates main receiver task, returns immedieately if already started
        self._startReceiver(shutdownEvent, sharedQueue)

        clientQueue = Queue()
        trace("Created client queue")

        client: iClient | None = None
        try:            
            process: Process = self._startProcess(
                worker, shutdownEvent, clientQueue, sharedQueue, handler
            )
            identity: int = process.ident

            client: iClient = clientType(clientId=identity)
            self.clients[identity] = client
            return client

        except Exception as ex:
            self._resourceCleanup(client.identity, sharedQueue, clientQueue)
            raise

    def running(self, clientId: str | None = None) -> bool:
        if clientId is not None:
            process = self._clients.get(clientId)
            return process is not None and process.is_alive()

        return (
            self._shutdownEvent is not None
            and not self._shutdownEvent.is_set()
            and len(self._clients) > 0
        )

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

    def _resourceCleanup(self, clientId: str, sharedQueue: Queue, clientQueue: Queue) -> None:
        try:
            drainQueue(clientQueue)            
            closeQueue(clientQueue)

        except Exception:  # noqa: BLE001, S110
            pass

        def _getProcessById(pid: int):
            return next(
                (process for process in active_children()
                if process.ident == pid),
                None
            )
        client: iClient = self.clients.pop(clientId, None)        
        if client is not None:            
            process: Process = _getProcessById(clientId)

            if process is not None:
                if process.is_alive():
                    process.terminate()
                    process.join()
            
                process.close()

        if not self.clients:
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

    async def _handleMessage(self, message: iMessage) -> None:
        clientId: int = message.ownerId
        if clientId not in self.clients:
            raise ClientNotFoundException(clientId, f"Client not found: [{clientId}]")

        client: iClient = self.clients[clientId]
        if isinstance(message, Handshake):
            trace(f"Handshake message recieved from [{clientId}]; type: [{type(message).__name__}]", color="cyan")
            message.payload = "ACKNOWLEDGED"
            await self._dispatch(clientId, message)
            client.beat(2.0)

        await client.push(message)

    def _startProcess(
        self, _worker: Callable[..., Awaitable], shutdownEvent: syncEvent,
        clientQueue: Queue, sharedQueue: Queue, handler: handlerType
    ) -> Process:
        async def worker(self, shutdownEvent, *args, **kwargs): ...
        worker: Callable[..., Awaitable] = _worker
        
        process = Process(
            target=processEntry,
            args=(worker, (shutdownEvent, clientQueue, sharedQueue, handler), {}),
            daemon=True,
            name=f"PROC_{uuid4().hex}",
        )
        process.start()
        self._outQueues[process.ident] = clientQueue
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
                cleanUpTask: dict[str, bool] = {
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

                    except Exception:  # noqa: BLE001, S110
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

        except Exception as ex:  # noqa: BLE001
            task.get_loop().call_exception_handler(
                {
                    "message": f"ProcessHost '{self.name}' stopAsync failed",
                    "exception": ex, "task": task,
                }
            )

        finally:
            if self._stopTask is task:
                self._stopTask = None
    
    def _closeQueues(self) -> None:
        queues: list[Queue] = list(self._outQueues.values())
        for lQueue in queues:
            try:
                closeQueue(lQueue)

            except Exception:  # noqa: BLE001, S110
                pass

        self._outQueues.clear()

        try:
            closeQueue(self._inQueue)

        except Exception:  # noqa: BLE001, S110
            pass

        self._inQueue = None
        self._receiverTask = None

# ==================================================================================
__all__ = ["ProcessHost"]
