# ==================================================================================
from __future__ import annotations

# ==================================================================================
import inspect

# ==================================================================================
from asyncio import Queue as asyncQueue
from asyncio import Task
from asyncio import sleep as asyncSleep
from asyncio.queues import QueueEmpty
from threading import Lock, RLock
from time import monotonic_ns
from typing import Optional, Union

# ==================================================================================
from ...services import Subscription
from ...types import eClientState
from ...types.interface.communication import iProcessHost
from ...types.interface.communication.client import iClient
from ...types.interface.communication.messages import iMessage
from ..__helper import drainQueue
from ..message import Heartbeat, Terminated

# ==================================================================================
QUEUE_SIZE: int = 32
DEFAULT_EXPIRY: float = 2.0
ENDSIGNAL: object = object()
# ==================================================================================

# ==================================================================================
# iClient is a runtime_checkable Protocol; its metaclass must be a base of ours
# to avoid "metaclass conflict" when Client inherits iClient + Subscription.
class _ClientMeta(type(iClient)):
    def __call__(cls, *args, **kwargs):
        if not Client._isCalledFromAllowedFactory():
            raise RuntimeError(
                "Client and all subclasses MUST be created inside ProcessHost.start."
            )
        return super().__call__(*args, **kwargs)


class Client(iClient, Subscription, metaclass=_ClientMeta):
    def __init__(self, clientId: int):
        super().__init__()

        self._expiry: int = int(DEFAULT_EXPIRY * 1e9) + monotonic_ns()
        self._identity: int = clientId

        self._clientState: eClientState = eClientState.PENDING
        self._expiryTask: Optional[Task] = None
        self._messageQueue: asyncQueue = asyncQueue(QUEUE_SIZE)
        self._queueTask: Optional[Task] = None
        self._beatLock: Lock = Lock()

    def beat(self, expiry: float = 0.1) -> None:
        with self._beatLock:
            # Margin large enough to absorb multiprocessing queue + to_thread + asyncio scheduling latency.
            MARGIN: float = 1.0
            safeExpiry: float = max(0.05, expiry + MARGIN)

            durationNs: int = int(safeExpiry * 1e9)
            now: int = monotonic_ns()

            self._expiry = now + durationNs

            # Cancel previous expiry (its done callback must be ignored)
            oldTask: Optional[Task] = self._expiryTask
            if oldTask is not None and not oldTask.done():
                self._expiryTask = None
                oldTask.cancel()

            def _expire(task: Task) -> None:
                # Ignore cancelled tasks and any task that is no longer current
                if task.cancelled() or task is not self._expiryTask:
                    return
                # A newer beat (including the Handshake ACK) has already extended the deadline
                if monotonic_ns() < self._expiry:
                    return
                trace("Heartbeat expired")
                self.clientState = eClientState.DORMANT

            newTask: Task = createTask(asyncSleep, safeExpiry)
            newTask.add_done_callback(_expire)
            self._expiryTask = newTask
            self.clientState = eClientState.ACTIVE

    async def push(self, message: iMessage) -> None:
        queue: asyncQueue = self._messageQueue
        messageType: str = type(message).__name__
        state: eClientState = self.clientState

        # DORMANT is recoverable: its message processor remains alive. Do not
        # discard device/domain messages merely because the heartbeat deadline
        # expired; the next Heartbeat will restore ACTIVE independently.
        shouldQueue: bool = (state is eClientState.ACTIVE or isinstance(message, (Heartbeat, Terminated)))

        if shouldQueue:
            if queue.full():
                dropped: Union[iMessage, object] = await queue.get()
                verbose(f"Client queue full; discarded oldest={type(dropped).__name__} before enqueueing={messageType}")
        
            await queue.put(message)
            verbose(f"Client queued message={messageType} state={state.name} queueSize={queue.qsize()}")
            return

        verbose(f"Client dropped message={messageType} state={state.name}")

    async def processMessage(self, message: iMessage, handled: bool = False):        
        if handled: return
        if isinstance(message, Heartbeat):
            verbose(f"Heartbeat received {self.clientState.name}")
            self.beat(float(message.payload))

        if isinstance(message, Terminated):
            verbose(f"process termination recieved [{self.identity}]")
            self.clientState = eClientState.TERMINATED

    async def _messageProc(self):
        queue: asyncQueue = self._messageQueue
        while True:
            msg: Union[iMessage, object] = await queue.get()
            if msg is ENDSIGNAL: break
            trace(f"Client MESSAGE RECEIVED... {type(msg).__name__}: {msg.payload}", color="yellow")
            await self.processMessage(msg, False)
            

    @property
    def clientState(self) -> eClientState:
        return self._clientState

    @clientState.setter
    def clientState(self, value: eClientState):
        assert isinstance(value, eClientState)
        if self._clientState != value:
            oldValue: eClientState = self._clientState
            self._clientState = value
            trace(f"State changed from {oldValue.name} to {value.name}")
            self.raiseEvent("STATE_CHANGED", value, oldValue)

        queueTask: Optional[Task] = self._queueTask
        # Only TERMINATED stops the processor. DORMANT must keep it alive so the
        # next Heartbeat can be processed and call beat() to recover.
        if value == eClientState.TERMINATED:
            if queueTask is not None and not queueTask.done():
                createTask(self._messageQueue.put, ENDSIGNAL)

        if queueTask is None or queueTask.done():
            try:
                drainQueue(self._messageQueue)

            except QueueEmpty:
                pass

            queueTask = createTask(self._messageProc)

            # If the processor exits while we are still ACTIVE, restart it.
            def _restart_if_active(done_task: Task) -> None:
                if done_task.cancelled(): return
                if (
                    self.clientState == eClientState.ACTIVE
                    and (self._queueTask is None or self._queueTask.done())
                ):
                    self.clientState = eClientState.ACTIVE

            queueTask.add_done_callback(_restart_if_active)

        self._queueTask = queueTask

    @property
    def identity(self) -> int:
        return self._identity

    @property
    def expiry(self) -> int:
        return self._expiry

    @staticmethod
    def _isCalledFromAllowedFactory() -> bool:
        frame = inspect.currentframe()
        try:
            # Walk until we find the caller of the constructor
            # Frame 0: _isCalledFromAllowedFactory
            # Frame 1: _ClientMeta.__call__
            # Frame 2: actual caller of Client(...) / subclass(...)
            callerFrame = frame.f_back.f_back if frame and frame.f_back else None
            if callerFrame is None:
                return False

            functionName = callerFrame.f_code.co_name
            me = callerFrame.f_locals.get("self")
            if me is None:
                return False

            return functionName == "start" and isinstance(me, iProcessHost)

        finally:
            del frame
