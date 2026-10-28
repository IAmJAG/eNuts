# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import (
    CancelledError,
    Event,
    Task,
    create_task,
    get_running_loop,
    sleep as asyncSleep,
    to_thread,
)
from asyncio import Queue as AsyncQueue
from queue import Empty
from time import monotonic
from typing import Any, Callable
from uuid import UUID

# ==================================================================================
from ..types.interface.communication import iBridge, iEndpoint, iIOQueue, iMessage
from .__overload import OverloadPolicy


# ==================================================================================
class Endpoint(iEndpoint):
    """Process-local IPC endpoint.

    Owns the IOQueue adapter and routes inbound messages to Bridges by
    ``message.ownerId``. Correlation lifecycle is entirely Bridge-owned.

    Peer liveness (``_bridgeAlive``) is keyed by peer ``bridgeId`` (the id the
    peer stamps as ``ownerId``). Local bridges live in ``_bridges``.
    """

    C_RECEIVE_TIMEOUT: float = 0.01
    C_ERROR_BACKOFF_BASE_S: float = 0.01
    C_ERROR_BACKOFF_MAX_S: float = 0.5

    def __init__(
        self,
        ioQueue: iIOQueue,
        *,
        overloadPolicy: OverloadPolicy = OverloadPolicy.UNBOUNDED,
        outboundCapacity: int | None = None,
    ) -> None:
        if outboundCapacity is not None and outboundCapacity <= 0:
            raise ValueError("outboundCapacity must be positive or None")

        self._ioQueue: iIOQueue = ioQueue
        self._outbound: AsyncQueue[iMessage] | None = None
        self._inboundTask: Task | None = None
        self._outboundTask: Task | None = None
        self._stopping: Event = Event()
        self._started: bool = False
        self._errorStreak: int = 0

        self._bridges: dict[UUID, iBridge] = {}
        self._defaultBridgeId: UUID | None = None
        self._bridgeAlive: dict[UUID, float] = {}  # peer bridgeId → expiry (monotonic)

        self._overloadPolicy: OverloadPolicy = overloadPolicy
        self._outboundCapacity: int | None = outboundCapacity

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def isStarted(self) -> bool:
        return self._started

    @property
    def defaultBridgeId(self) -> UUID | None:
        return self._defaultBridgeId

    @property
    def overloadPolicy(self) -> OverloadPolicy:
        return self._overloadPolicy

    @overloadPolicy.setter
    def overloadPolicy(self, value: OverloadPolicy) -> None:
        self._overloadPolicy = value

    @property
    def outboundCapacity(self) -> int | None:
        return self._outboundCapacity

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    async def start(self) -> None:
        if self._started:
            raise RuntimeError("Endpoint is already started")

        self._stopping.clear()
        self._errorStreak = 0

        maxsize = 0  # asyncio.Queue: 0 == unbounded
        if (
            self._overloadPolicy is not OverloadPolicy.UNBOUNDED
            and self._outboundCapacity is not None
        ):
            maxsize = self._outboundCapacity

        self._outbound = AsyncQueue(maxsize=maxsize)
        self._inboundTask = create_task(self._pollInbound(), name="Endpoint.inbound")
        self._outboundTask = create_task(self._drainOutbound(), name="Endpoint.outbound")
        self._started = True

    async def stop(self, *, drainTimeout: float = 1.0) -> None:
        if not self._started:
            return

        self._stopping.set()

        await self._drainOutboundRemaining(drainTimeout)

        for task in (self._inboundTask, self._outboundTask):
            if task is not None and not task.done():
                task.cancel()

        for task in (self._inboundTask, self._outboundTask):
            if task is not None:
                try:
                    await task
                except CancelledError:
                    pass

        try:
            self._ioQueue.close()
            self._ioQueue.cancelJoinThread()
        except Exception:
            pass

        self._inboundTask = None
        self._outboundTask = None
        self._outbound = None
        self._started = False

    async def _drainOutboundRemaining(self, drainTimeout: float) -> None:
        outbound = self._outbound
        if outbound is None:
            return

        loop = get_running_loop()
        deadline = loop.time() + max(0.0, drainTimeout)
        send = self._ioQueue.send

        while not outbound.empty():
            if loop.time() >= deadline:
                break
            try:
                message = outbound.get_nowait()
            except Exception:
                break
            try:
                await to_thread(send, message)
            except Exception as ex:
                self._onTransportError(ex, where="drain")
                break

    # ------------------------------------------------------------------
    # Send (overload-aware)
    # ------------------------------------------------------------------
    async def send(self, message: iMessage) -> None:
        if not self._started or self._outbound is None:
            raise RuntimeError("Endpoint is not started")

        policy = self._overloadPolicy
        q = self._outbound

        if policy is OverloadPolicy.UNBOUNDED or q.maxsize == 0:
            await q.put(message)
            return

        if policy is OverloadPolicy.BLOCK:
            await q.put(message)
            return

        if policy is OverloadPolicy.DROP_NEW:
            if q.full():
                self._onTransportError(
                    RuntimeError("outbound full; DROP_NEW"),
                    where="outbound",
                )
                return
            await q.put(message)
            return

        if policy is OverloadPolicy.DROP_OLD:
            while q.full():
                try:
                    q.get_nowait()
                except Exception:
                    break
            await q.put(message)
            return

        await q.put(message)

    # ------------------------------------------------------------------
    # Bridge registry
    # ------------------------------------------------------------------
    def registerBridge(self, bridge: iBridge, *, asDefault: bool = False) -> None:
        bridgeId = bridge.bridgeId
        if bridgeId in self._bridges:
            raise ValueError(f"Bridge ID '{bridgeId}' is already registered")

        self._bridges[bridgeId] = bridge
        bridge.attachEndpoint(self)

        if asDefault:
            self._defaultBridgeId = bridgeId

    def unregisterBridge(self, bridge: iBridge) -> None:
        bridgeId = bridge.bridgeId
        if self._bridges.get(bridgeId) is not bridge:
            return

        del self._bridges[bridgeId]
        if self._defaultBridgeId == bridgeId:
            self._defaultBridgeId = None
        self._bridgeAlive.pop(bridgeId, None)

        bridge.detachEndpoint()

    def _resolveBridge(self, message: iMessage) -> iBridge | None:
        ownerId = message.ownerId
        if ownerId is None:
            if self._defaultBridgeId is None:
                return None
            return self._bridges.get(self._defaultBridgeId)

        return self._bridges.get(ownerId)

    # ------------------------------------------------------------------
    # Peer alive (bridgeId namespace — peer ownerId)
    # ------------------------------------------------------------------
    def markBridgeAlive(self, bridgeId: UUID, ttlS: float) -> None:
        """Mark a peer bridgeId alive until now + ttlS (monotonic seconds)."""
        if ttlS <= 0:
            raise ValueError("ttlS must be positive")
        self._bridgeAlive[bridgeId] = monotonic() + ttlS

    def isBridgeAlive(self, bridgeId: UUID) -> bool:
        expiry = self._bridgeAlive.get(bridgeId)
        if expiry is None:
            return False
        if monotonic() > expiry:
            self._bridgeAlive.pop(bridgeId, None)
            return False
        return True

    def sweepDeadBridges(self) -> list[UUID]:
        now = monotonic()
        dead = [bid for bid, exp in self._bridgeAlive.items() if now > exp]
        for bid in dead:
            self._bridgeAlive.pop(bid, None)
        return dead

    # ------------------------------------------------------------------
    # Error handling
    # ------------------------------------------------------------------
    def _onTransportError(self, ex: BaseException, *, where: str) -> None:
        self._errorStreak += 1
        # Project logger can be wired later; keep dependency-light for now.
        _ = (where, ex, self._errorStreak)

    async def _errorBackoff(self) -> None:
        n = min(self._errorStreak, 6)
        delay = min(
            self.C_ERROR_BACKOFF_BASE_S * (2**n),
            self.C_ERROR_BACKOFF_MAX_S,
        )
        await asyncSleep(delay)

    # ------------------------------------------------------------------
    # Inbound / outbound loops
    # ------------------------------------------------------------------
    async def _pollInbound(self) -> None:
        timeOut: float = self.C_RECEIVE_TIMEOUT
        receive: Callable[[float | None], Any] = self._ioQueue.receive
        isSet: Callable[[], bool] = self._stopping.is_set

        while not isSet():
            try:
                message = await to_thread(receive, timeOut)
            except Empty:
                continue
            except CancelledError:
                break
            except Exception as ex:
                self._onTransportError(ex, where="receive")
                if isSet():
                    break
                await self._errorBackoff()
                continue

            try:
                await self._onInbound(message)
                self._errorStreak = 0
            except CancelledError:
                break
            except Exception as ex:
                self._onTransportError(ex, where="dispatch")
                if isSet():
                    break
                await self._errorBackoff()

    async def _drainOutbound(self) -> None:
        outbound = self._outbound
        if outbound is None:
            return

        send: Callable[[iMessage], None] = self._ioQueue.send
        isSet: Callable[[], bool] = self._stopping.is_set

        while not isSet():
            try:
                message = await outbound.get()
            except CancelledError:
                break

            try:
                await to_thread(send, message)
                self._errorStreak = 0
            except CancelledError:
                break
            except Exception as ex:
                self._onTransportError(ex, where="outbound")
                if isSet():
                    break
                await self._errorBackoff()

    async def _onInbound(self, message: iMessage) -> None:
        bridge = self._resolveBridge(message)
        if bridge is None:
            return

        await bridge.handleMessage(message)


# ==================================================================================
__all__ = ["Endpoint"]
